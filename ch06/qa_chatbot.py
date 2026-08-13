# -*- coding: utf-8 -*-
"""실습: 문서 QA 챗봇 — 검색 + LLM = RAG 완성.

흐름: 질문 -> BM25 검색으로 관련 규정 청크 3개 -> 프롬프트에 넣어 LLM에 전달
      -> 규정에 근거한 답변 + 출처 표시

OpenAI API 키가 필요합니다 (.env 파일 또는 환경변수 OPENAI_API_KEY).
실행:  python qa_chatbot.py        (대화형, 종료는 'q')
"""
import os
import sys

from dotenv import load_dotenv
from openai import OpenAI

from bm25_search import search

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()
if not os.getenv("OPENAI_API_KEY"):
    sys.exit("OPENAI_API_KEY가 없습니다. .env 파일을 확인하세요. (03-2 참조)")

client = OpenAI()
MODEL = "gpt-4o-mini"

SYSTEM_PROMPT = """당신은 한빛제조(가상 회사)의 사내 규정 안내 챗봇입니다.

규칙:
1. 아래 [규정 발췌]에 있는 내용만으로 답하세요.
2. 발췌에 없는 내용은 "규정에서 찾지 못했습니다. 담당 부서에 문의해 주세요"라고 답하세요.
3. 답변 끝에 근거 규정을 (출처: 문서명#조항) 형식으로 표시하세요.
"""


def answer(question: str) -> str:
    results = search(question, top_k=3)
    context = "\n\n".join(
        f"[{chunk['id']}]\n{chunk['text']}" for _, chunk in results)
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",
             "content": f"[규정 발췌]\n{context}\n\n[질문]\n{question}"},
        ],
        temperature=0,
    )
    return resp.choices[0].message.content


if __name__ == "__main__":
    print("한빛제조 규정 챗봇입니다. 질문을 입력하세요. (종료: q)")
    while True:
        question = input("\n질문> ").strip()
        if question.lower() in ("q", "quit", "exit"):
            break
        if question:
            print("\n" + answer(question))
