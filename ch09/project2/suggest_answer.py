# -*- coding: utf-8 -*-
"""프로젝트 2 (2단계): 과거 답변 검색 — 신입 상담원 지원 도구.

고객 요구: "신입 상담원이 답을 몰라서 매번 선배에게 물어봐요."
전략: 과거 상담 로그가 곧 지식 베이스다. 새 문의가 오면
      비슷한 과거 문의를 찾아 그때의 답변을 보여준다. (6장 BM25 재사용)

실행:  python suggest_answer.py "배송이 너무 늦어요"
"""
import re
import sys

import pandas as pd
from rank_bm25 import BM25Okapi

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def tokenize(text: str) -> list[str]:
    words = re.findall(r"[가-힣a-zA-Z0-9]+", str(text).lower())
    bigrams = []
    for w in words:
        bigrams.extend(w[i:i + 2] for i in range(len(w) - 1))
    return words + bigrams


df = pd.read_csv("data/consult_logs_labeled.csv")
bm25 = BM25Okapi([tokenize(q) for q in df["문의내용"]])


def suggest(question: str, top_k: int = 3):
    scores = bm25.get_scores(tokenize(question))
    top = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
    return [(scores[i], df.iloc[i]) for i in top if scores[i] > 0]


if __name__ == "__main__":
    question = sys.argv[1] if len(sys.argv) > 1 else "배송이 너무 늦어요"
    print(f"새 문의: {question}\n")
    results = suggest(question)
    if not results:
        print("비슷한 과거 상담이 없습니다 — 선배 상담원에게 에스컬레이션")
    for rank, (score, row) in enumerate(results, 1):
        print(f"{rank}위 (점수 {score:.2f}) [{row['카테고리']}] {row['문의내용']}")
        print(f"    당시 답변: {row['답변내용']}\n")
