# -*- coding: utf-8 -*-
"""실습 2: BM25 키워드 검색 — 임베딩 없이 시작하는 검색.

BM25는 '질문의 단어가 문서에 얼마나 등장하는가'로 점수를 매기는
고전적인 검색 알고리즘입니다. API 비용이 들지 않고 폐쇄망에서도 돌아서,
FDE가 고객사에서 검색 품질의 기준선(baseline)을 잡을 때 유용합니다.

실행:  python bm25_search.py "질문"
"""
import json
import re
import sys
from pathlib import Path

from rank_bm25 import BM25Okapi

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def tokenize(text: str) -> list[str]:
    """한국어 간이 토크나이저: 공백 분리 + 2글자 문자 조각(bigram) 추가.

    형태소 분석기 없이도 '재택근무를'과 '재택근무' 같은
    조사 차이를 bigram이 어느 정도 흡수해 줍니다.
    """
    words = re.findall(r"[가-힣a-zA-Z0-9]+", text.lower())
    bigrams = []
    for w in words:
        bigrams.extend(w[i:i + 2] for i in range(len(w) - 1))
    return words + bigrams


chunks = json.loads(Path("chunks.json").read_text(encoding="utf-8"))
corpus = [tokenize(f"{c['doc_title']} {c['heading']} {c['text']}") for c in chunks]
bm25 = BM25Okapi(corpus)


def search(query: str, top_k: int = 3) -> list[tuple[float, dict]]:
    scores = bm25.get_scores(tokenize(query))
    ranked = sorted(zip(scores, chunks), key=lambda x: x[0], reverse=True)
    return ranked[:top_k]


if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else "재택근무는 주 몇 회까지 가능한가요?"
    print(f"질문: {query}\n")
    for rank, (score, chunk) in enumerate(search(query), 1):
        print(f"{rank}위 (점수 {score:.2f}) [{chunk['id']}]")
        print(f"   {chunk['text'][:80]}...")
        print()
