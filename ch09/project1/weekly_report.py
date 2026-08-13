# -*- coding: utf-8 -*-
"""프로젝트 1: 주간 품질 리포트 자동화.

고객 요구(04장 경영 보고 회의록에서 나온 것):
"매주 월요일 아침에 지난주 품질 요약이 자동으로 나오는 체계를 만들 것."

구성: 5장 ETL 파이프라인 -> 통계 분석 -> 마크다운 리포트 생성
LLM 코멘트는 선택 사항 — 키가 없어도 리포트는 나온다 (핵심 기능 우선).

실행:  python weekly_report.py 2026-07-06 2026-07-11
"""
import os
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()
DATA_PATH = "../../ch05/output/quality_cleaned.csv"


def analyze(start: str, end: str) -> dict:
    """지난주 데이터에서 리포트에 들어갈 숫자를 뽑는다."""
    df = pd.read_csv(DATA_PATH)
    df["검사일자"] = pd.to_datetime(df["검사일자"])
    week = df[df["검사일자"].between(start, end)]

    by_line = week.groupby("라인").agg(
        검사수=("판정", "size"),
        불량수=("판정", lambda s: (s == "불합격").sum()),
        평균측정=("측정값(mm)", "mean"),
    )
    by_line["불량률(%)"] = (by_line["불량수"] / by_line["검사수"] * 100).round(1)

    worst_line = by_line["불량률(%)"].idxmax()
    fails = week[week["판정"] == "불합격"]
    return {"week": week, "by_line": by_line,
            "worst_line": worst_line, "fails": fails}


def llm_comment(stats_md: str) -> str:
    """LLM이 있으면 경영진용 코멘트를 덧붙인다. 없으면 건너뛴다."""
    if not os.getenv("OPENAI_API_KEY"):
        return "(LLM 코멘트 생략 — OPENAI_API_KEY 미설정)"
    from openai import OpenAI
    client = OpenAI()
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user",
                   "content": "다음 품질 통계를 보고 경영진에게 전할 "
                              "핵심 코멘트를 3줄로 써 주세요. 과장 없이, "
                              "숫자에 근거해서:\n\n" + stats_md}],
        temperature=0,
    )
    return resp.choices[0].message.content


def build_report(start: str, end: str) -> str:
    r = analyze(start, end)
    stats_md = r["by_line"].round(2).to_markdown()

    lines = [
        f"## 주간 품질 리포트 ({start} ~ {end})",
        f"",
        f"생성: {datetime.now().strftime('%Y-%m-%d %H:%M')} (자동 생성)",
        f"",
        f"### 요약",
        f"- 총 검사 {len(r['week'])}건, 불량 {len(r['fails'])}건",
        f"- 불량률 최고 라인: **{r['worst_line']}라인** "
        f"({r['by_line'].loc[r['worst_line'], '불량률(%)']}%)",
        f"",
        f"### 라인별 현황",
        stats_md,
        f"",
        f"### 불량 상세",
        r["fails"][["검사일자", "라인", "제품코드", "측정값(mm)", "검사자"]]
        .to_markdown(index=False),
        f"",
        f"### 코멘트",
        llm_comment(stats_md),
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    start = sys.argv[1] if len(sys.argv) > 1 else "2026-07-06"
    end = sys.argv[2] if len(sys.argv) > 2 else "2026-07-11"
    report = build_report(start, end)
    out = Path(f"report_{start}_{end}.md")
    out.write_text(report, encoding="utf-8")
    print(report)
    print(f"\n=> {out} 저장 완료")
