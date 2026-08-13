# -*- coding: utf-8 -*-
"""에이전트에게 줄 도구(tool) 모음.

도구는 그냥 파이썬 함수입니다. 에이전트가 스스로 판단해서 호출합니다.
5장에서 만든 품질 데이터(quality_cleaned.csv)를 조회·분석하는 도구 3개와,
'위험한' 도구(리포트 발송) 1개를 준비합니다.
"""
import json

import pandas as pd

DATA_PATH = "../ch05/output/quality_cleaned.csv"


def query_quality(start_date: str, end_date: str, line: str = "") -> str:
    """기간(과 라인)으로 품질 검사 데이터를 조회한다."""
    df = pd.read_csv(DATA_PATH)
    df["검사일자"] = pd.to_datetime(df["검사일자"])
    mask = df["검사일자"].between(start_date, end_date)
    if line:
        mask &= df["라인"] == line.upper()
    result = df[mask].copy()
    result["검사일자"] = result["검사일자"].dt.strftime("%Y-%m-%d")
    return result.to_json(orient="records", force_ascii=False)


def calc_defect_rate(start_date: str, end_date: str) -> str:
    """기간 내 라인별 불량률을 계산한다."""
    df = pd.read_csv(DATA_PATH)
    df["검사일자"] = pd.to_datetime(df["검사일자"])
    df = df[df["검사일자"].between(start_date, end_date)]
    if df.empty:
        return json.dumps({"error": "해당 기간에 데이터가 없습니다"},
                          ensure_ascii=False)
    rate = (df.groupby("라인")["판정"]
            .apply(lambda s: round((s == "불합격").mean() * 100, 1)))
    return json.dumps({"라인별 불량률(%)": rate.to_dict(),
                       "전체 검사 건수": len(df)}, ensure_ascii=False)


def send_report(recipient: str, subject: str, body: str) -> str:
    """품질 리포트를 발송한다. (실습에서는 실제 발송 대신 파일로 저장)

    주의: 외부로 나가는 행동이므로 에이전트 루프에서 사람의 승인을 거친다.
    """
    with open("sent_report.txt", "w", encoding="utf-8") as f:
        f.write(f"받는 사람: {recipient}\n제목: {subject}\n\n{body}")
    return json.dumps({"status": "발송 완료", "to": recipient},
                      ensure_ascii=False)


# LLM에게 알려줄 도구 명세 (OpenAI tool calling 형식)
TOOL_SPECS = [
    {"type": "function", "function": {
        "name": "query_quality",
        "description": "기간과 라인으로 품질 검사 데이터를 조회한다",
        "parameters": {"type": "object", "properties": {
            "start_date": {"type": "string", "description": "YYYY-MM-DD"},
            "end_date": {"type": "string", "description": "YYYY-MM-DD"},
            "line": {"type": "string", "description": "라인명(A/B/C). 생략 시 전체"},
        }, "required": ["start_date", "end_date"]}}},
    {"type": "function", "function": {
        "name": "calc_defect_rate",
        "description": "기간 내 라인별 불량률(%)을 계산한다",
        "parameters": {"type": "object", "properties": {
            "start_date": {"type": "string"}, "end_date": {"type": "string"},
        }, "required": ["start_date", "end_date"]}}},
    {"type": "function", "function": {
        "name": "send_report",
        "description": "품질 리포트를 이메일로 발송한다",
        "parameters": {"type": "object", "properties": {
            "recipient": {"type": "string"}, "subject": {"type": "string"},
            "body": {"type": "string"},
        }, "required": ["recipient", "subject", "body"]}}},
]

TOOL_FUNCTIONS = {
    "query_quality": query_quality,
    "calc_defect_rate": calc_defect_rate,
    "send_report": send_report,
}

# 사람 승인이 필요한 도구 목록 — 외부로 나가거나 되돌리기 어려운 행동
NEEDS_APPROVAL = {"send_report"}
