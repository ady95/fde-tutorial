# -*- coding: utf-8 -*-
"""실습 3: 임베딩 검색 — 단어가 아니라 의미로 찾는다.

BM25는 '단어가 겹쳐야' 찾지만, 임베딩 검색은 '뜻이 비슷하면' 찾습니다.
예: "집에서 일해도 되나요?" -> 재택근무 규정 (단어가 하나도 안 겹쳐도)

OpenAI API 키가 필요합니다 (.env 파일 또는 환경변수 OPENAI_API_KEY).
실행:  python embedding_search.py "질문"
"""
import json
import os
import sys
from pathlib import Path

import numpy as np
from dotenv import load_dotenv
from openai import OpenAI

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()
if not os.getenv("OPENAI_API_KEY"):
    sys.exit("OPENAI_API_KEY가 없습니다. .env 파일을 확인하세요. (03-2 참조)")

client = OpenAI()
MODEL = "text-embedding-3-small"

chunks = json.loads(Path("chunks.json").read_text(encoding="utf-8"))


def embed(texts: list[str]) -> np.ndarray:
    """텍스트 목록을 임베딩 벡터로 변환한다."""
    resp = client.embeddings.create(model=MODEL, input=texts)
    return np.array([d.embedding for d in resp.data])


# 1) 전체 청크를 한 번에 임베딩하고 캐시 (매번 API를 부르면 느리고 비싸다)
cache = Path("embeddings.npy")
if cache.exists():
    doc_vectors = np.load(cache)
else:
    texts = [f"{c['doc_title']} {c['heading']}\n{c['text']}" for c in chunks]
    doc_vectors = embed(texts)
    np.save(cache, doc_vectors)
    print(f"청크 {len(chunks)}개 임베딩 완료 (모델: {MODEL})")


def search(query: str, top_k: int = 3):
    """코사인 유사도로 가장 가까운 청크를 찾는다."""
    q = embed([query])[0]
    sims = doc_vectors @ q / (
        np.linalg.norm(doc_vectors, axis=1) * np.linalg.norm(q))
    top = np.argsort(sims)[::-1][:top_k]
    return [(float(sims[i]), chunks[i]) for i in top]


if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else "집에서 일해도 되나요?"
    print(f"질문: {query}\n")
    for rank, (score, chunk) in enumerate(search(query), 1):
        print(f"{rank}위 (유사도 {score:.3f}) [{chunk['id']}]")
        print(f"   {chunk['text'][:80]}...")
        print()
