# -*- coding: utf-8 -*-
"""실습 2: 데이터 정제 — 프로파일링에서 찾은 문제를 하나씩 해결한다.

정제의 원칙: 원본은 절대 덮어쓰지 않는다. 정제 결과는 새 파일로 저장한다.
"""
import sys

import pandas as pd

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def parse_measure(value):
    """측정값 통일: '1.26cm' -> 12.6(mm), '12,6' -> 12.6, 공란 -> NaN"""
    if pd.isna(value):
        return None
    s = str(value).strip().replace(",", ".")
    if s.endswith("cm"):
        return float(s[:-2]) * 10
    if s.endswith("mm"):
        return float(s[:-2])
    return float(s)


df = pd.read_csv("data/quality_raw.csv", encoding="cp949")
before = len(df)

# 1) 컬럼명 공백 제거 ('검사자 ' -> '검사자')
df.columns = df.columns.str.strip()

# 2) 완전 중복 행 제거
df = df.drop_duplicates()

# 3) 날짜 형식 통일 — 형식이 섞여 있으므로 format='mixed'
df["검사일자"] = pd.to_datetime(df["검사일자"], format="mixed")

# 4) 라인 표기 통일: 'a', 'A라인' -> 'A'
df["라인"] = df["라인"].str.upper().str.replace("라인", "", regex=False).str.strip()

# 5) 측정값: 단위(cm/mm)·콤마 소수점 통일
df["측정값(mm)"] = df["측정값(mm)"].map(parse_measure)

# 6) 판정 표기 통일: PASS/OK/pass -> 합격, FAIL -> 불합격
judge_map = {"PASS": "합격", "OK": "합격", "FAIL": "불합격"}
df["판정"] = df["판정"].str.upper().map(lambda x: judge_map.get(x, x))

# 7) 결측치 처리 — 지우지 말고 고객에게 물어볼 목록으로 분리
missing = df[df["측정값(mm)"].isna() | df["검사자"].isna()]
missing.to_csv("data/quality_needs_check.csv", index=False, encoding="utf-8-sig")
cleaned = df.dropna(subset=["측정값(mm)"])

cleaned.to_csv("data/quality_cleaned.csv", index=False, encoding="utf-8-sig")

print(f"원본 {before}행 -> 정제 {len(cleaned)}행")
print(f"확인 필요(결측 포함) {len(missing)}행 -> data/quality_needs_check.csv")
print()
print("정제 후 요약:")
print(cleaned.groupby(["라인", "판정"]).size().unstack(fill_value=0).to_string())
print()
print(f"측정값 평균 {cleaned['측정값(mm)'].mean():.2f}mm / "
      f"표준편차 {cleaned['측정값(mm)'].std():.2f}")
