# -*- coding: utf-8 -*-
"""실습 3: 온톨로지 — 도메인을 코드로 구조화한다.

온톨로지는 "이 회사의 세계에는 어떤 사물(객체)이 있고, 서로 어떻게
연결되며, 무엇을 할 수 있는가"를 정의한 지도입니다.
팔란티어 파운드리의 핵심 개념을 아주 작은 규모로 흉내 내 봅니다.

구성:
- 객체 타입(Object Type): 설비, 검사로트, 작업자
- 관계(Link): 검사로트 -> 설비(에서 생산), 검사로트 -> 작업자(가 검사)
- 액션(Action): 설비 점검 요청 — 누가, 무엇을, 어떤 조건에서 할 수 있는지 명시

실행:  python ontology.py
"""
import sys
from dataclasses import dataclass, field

import pandas as pd

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


# ── 객체 타입 정의 ────────────────────────────────────────────

@dataclass
class Equipment:
    """설비: 제조 라인의 물리적 실체"""
    line_id: str            # A, B, C
    name: str
    installed_year: int
    lots: list = field(default_factory=list)   # 관계: 이 설비가 생산한 로트들


@dataclass
class InspectionLot:
    """검사 로트: 품질 검사의 단위"""
    lot_id: str
    date: str
    measure_mm: float
    passed: bool
    equipment: "Equipment" = None       # 관계: 어느 설비에서 생산됐나
    inspector: "Inspector" = None       # 관계: 누가 검사했나


@dataclass
class Inspector:
    """작업자: 검사를 수행하는 사람"""
    name: str
    certified: bool = True


# ── 액션 정의: '할 수 있는 일'에도 규칙이 있다 ─────────────────

def request_maintenance(equipment: Equipment, reason: str,
                        requester: Inspector) -> str:
    """설비 점검 요청 액션.

    거버넌스 규칙:
    1) 인증된 검사자만 요청할 수 있다
    2) 요청 사유가 있어야 한다
    실제 시스템이라면 이 액션이 감사 로그에 남고, 승인 절차로 이어집니다.
    """
    if not requester.certified:
        return f"거부: {requester.name}은(는) 인증된 검사자가 아닙니다"
    if not reason.strip():
        return "거부: 요청 사유가 필요합니다"
    return (f"접수: {equipment.name}({equipment.line_id}라인) 점검 요청 "
            f"— 사유: {reason} / 요청자: {requester.name}")


# ── 데이터를 온톨로지 객체로 변환 ─────────────────────────────

def build_ontology(csv_path: str):
    df = pd.read_csv(csv_path)

    equipments = {line: Equipment(line, f"{line}라인 프레스", 2018 + i)
                  for i, line in enumerate(sorted(df["라인"].unique()))}
    inspectors = {name: Inspector(name)
                  for name in df["검사자"].dropna().unique()}

    lots = []
    for _, row in df.iterrows():
        lot = InspectionLot(
            lot_id=row["제품코드"], date=row["검사일자"],
            measure_mm=row["측정값(mm)"], passed=(row["판정"] == "합격"),
            equipment=equipments[row["라인"]],
            inspector=inspectors.get(row["검사자"]),
        )
        equipments[row["라인"]].lots.append(lot)   # 양방향 관계
        lots.append(lot)
    return equipments, inspectors, lots


if __name__ == "__main__":
    equipments, inspectors, lots = build_ontology(
        "../ch05/output/quality_cleaned.csv")

    print(f"온톨로지 구축: 설비 {len(equipments)} / "
          f"작업자 {len(inspectors)} / 검사로트 {len(lots)}\n")

    # 관계 탐색 1: 설비에서 출발해 불량 로트 찾기
    for eq in equipments.values():
        failed = [lot for lot in eq.lots if not lot.passed]
        print(f"{eq.name}: 로트 {len(eq.lots)}건 중 불량 {len(failed)}건")

    # 관계 탐색 2: 불량 로트에서 출발해 설비·작업자로 거슬러 가기
    worst = max(equipments.values(),
                key=lambda e: sum(not lot.passed for lot in e.lots))
    print(f"\n불량 최다 설비: {worst.name} (설치 {worst.installed_year}년)")
    for lot in worst.lots:
        if not lot.passed:
            print(f"  {lot.lot_id} ({lot.date}) 측정 {lot.measure_mm}mm "
                  f"/ 검사자 {lot.inspector.name}")

    # 액션 실행: 거버넌스 규칙이 적용된다
    print()
    me = inspectors["이서연"]
    print(request_maintenance(worst, "불량률 지속 상승", me))
    print(request_maintenance(worst, "", me))
