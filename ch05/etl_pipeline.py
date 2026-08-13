# -*- coding: utf-8 -*-
"""실습 3: 재실행 가능한 ETL 파이프라인.

일회성 스크립트와의 차이:
- 추출(extract) / 변환(transform) / 적재(load) 함수 분리
- 설정 파일(config.json)로 경로·규칙 외부화 -> 고객 환경에서 코드 수정 없이 적용
- 로깅 -> 새벽에 실패했을 때 원인을 찾을 수 있다
- 실패 처리 -> 잘못된 행을 버리지 않고 격리(quarantine)한다

실행:  python etl_pipeline.py config.json
"""
import json
import logging
import sys
from pathlib import Path

import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.StreamHandler(),
              logging.FileHandler("etl.log", encoding="utf-8")],
)
log = logging.getLogger("etl")


def extract(cfg: dict) -> pd.DataFrame:
    """원본 CSV를 읽는다. 인코딩 후보를 순서대로 시도한다."""
    src = cfg["source_csv"]
    for enc in cfg.get("encodings", ["utf-8", "cp949"]):
        try:
            df = pd.read_csv(src, encoding=enc)
            log.info("추출 완료: %s (%s, %d행)", src, enc, len(df))
            return df
        except UnicodeDecodeError:
            log.warning("인코딩 %s 실패 — 다음 후보 시도", enc)
    raise ValueError(f"지원 인코딩으로 읽을 수 없습니다: {src}")


def parse_measure(value):
    if pd.isna(value):
        return None
    s = str(value).strip().replace(",", ".")
    if s.endswith("cm"):
        return float(s[:-2]) * 10
    if s.endswith("mm"):
        return float(s[:-2])
    return float(s)


def transform(df: pd.DataFrame, cfg: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    """정제 규칙을 적용하고 (정상, 격리) 두 덩어리로 나눈다."""
    df = df.copy()
    df.columns = df.columns.str.strip()
    df = df.drop_duplicates()

    df["검사일자"] = pd.to_datetime(df["검사일자"], format="mixed")
    df["라인"] = (df["라인"].str.upper()
                  .str.replace("라인", "", regex=False).str.strip())
    df["측정값(mm)"] = df["측정값(mm)"].map(parse_measure)
    judge_map = {"PASS": "합격", "OK": "합격", "FAIL": "불합격"}
    df["판정"] = df["판정"].str.upper().map(lambda x: judge_map.get(x, x))

    # 검증 규칙: 측정값 범위 밖이거나 필수값 결측이면 격리
    lo, hi = cfg["measure_range"]
    bad = (df["측정값(mm)"].isna()
           | ~df["측정값(mm)"].between(lo, hi)
           | df["검사자"].isna())
    quarantine = df[bad]
    ok = df[~bad]
    log.info("변환 완료: 정상 %d행 / 격리 %d행", len(ok), len(quarantine))
    return ok, quarantine


def load(ok: pd.DataFrame, quarantine: pd.DataFrame, cfg: dict) -> None:
    """결과를 저장한다. 같은 입력이면 몇 번을 돌려도 결과가 같다(멱등)."""
    out = Path(cfg["output_dir"])
    out.mkdir(exist_ok=True)
    ok.to_csv(out / "quality_cleaned.csv", index=False, encoding="utf-8-sig")
    quarantine.to_csv(out / "quality_quarantine.csv", index=False,
                      encoding="utf-8-sig")
    log.info("적재 완료: %s (정상 %d / 격리 %d)", out, len(ok), len(quarantine))


def run(config_path: str) -> None:
    cfg = json.loads(Path(config_path).read_text(encoding="utf-8"))
    log.info("=== 파이프라인 시작 (config: %s) ===", config_path)
    try:
        df = extract(cfg)
        ok, quarantine = transform(df, cfg)
        load(ok, quarantine, cfg)
        log.info("=== 파이프라인 정상 종료 ===")
    except Exception:
        log.exception("파이프라인 실패 — 원인:")
        raise


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else "config.json")
