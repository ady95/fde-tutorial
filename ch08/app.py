# -*- coding: utf-8 -*-
"""실습: 품질 분석 기능을 API 서비스로 만든다.

스크립트는 '내가 실행'하지만, 서비스는 '고객사 시스템이 호출'합니다.
5장의 파이프라인 결과를 조회하는 API와 LLM 요약 API를 만듭니다.

실행:   uvicorn app:app --reload
문서:   http://127.0.0.1:8000/docs  (자동 생성되는 Swagger UI)
"""
import os
from datetime import date

import pandas as pd
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

load_dotenv()

app = FastAPI(
    title="한빛제조 품질 분석 API",
    description="FDE 실습용 — 품질 데이터 조회와 리포트 요약",
    version="0.1.0",
)

DATA_PATH = "../ch05/output/quality_cleaned.csv"


def load_data() -> pd.DataFrame:
    try:
        df = pd.read_csv(DATA_PATH)
    except FileNotFoundError:
        raise HTTPException(
            status_code=503,
            detail="데이터가 없습니다. ch05의 etl_pipeline.py를 먼저 실행하세요.")
    df["검사일자"] = pd.to_datetime(df["검사일자"])
    return df


@app.get("/health")
def health():
    """헬스체크 — 배포 후 모니터링이 이 주소를 주기적으로 확인한다."""
    return {"status": "ok"}


@app.get("/defect-rate")
def defect_rate(start: date, end: date):
    """기간 내 라인별 불량률을 반환한다.

    예: /defect-rate?start=2026-07-06&end=2026-07-11
    """
    df = load_data()
    df = df[df["검사일자"].between(str(start), str(end))]
    if df.empty:
        raise HTTPException(status_code=404, detail="해당 기간에 데이터가 없습니다")
    rate = (df.groupby("라인")["판정"]
            .apply(lambda s: round((s == "불합격").mean() * 100, 1)))
    return {"period": f"{start} ~ {end}",
            "defect_rate_percent": rate.to_dict(),
            "total_inspections": len(df)}


class SummarizeRequest(BaseModel):
    text: str = Field(..., min_length=10, description="요약할 텍스트")
    max_sentences: int = Field(3, ge=1, le=10)


@app.post("/summarize")
def summarize(req: SummarizeRequest):
    """텍스트를 LLM으로 요약한다. OPENAI_API_KEY가 있어야 동작한다."""
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(
            status_code=501,
            detail="OPENAI_API_KEY가 설정되지 않았습니다 (03-2 참조)")
    from openai import OpenAI
    client = OpenAI()
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user",
                   "content": f"다음 텍스트를 {req.max_sentences}문장 이내로 "
                              f"요약해 주세요:\n\n{req.text}"}],
        temperature=0,
    )
    return {"summary": resp.choices[0].message.content}
