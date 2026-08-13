# -*- coding: utf-8 -*-
"""첫 LLM API 호출 — 환경이 제대로 준비됐는지 확인한다.

실행 전 준비: .env 파일에 OPENAI_API_KEY=sk-... 를 저장 (03-2 참조)
실행:  python hello_llm.py
"""
import os
import sys

from dotenv import load_dotenv
from openai import OpenAI

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()                       # .env 파일을 환경변수로 읽어들인다
if not os.getenv("OPENAI_API_KEY"):
    sys.exit("OPENAI_API_KEY가 없습니다. .env 파일을 만들어 주세요.")

client = OpenAI()                   # 키는 환경변수에서 자동으로 읽는다

resp = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "user", "content": "FDE(Forward Deployed Engineer)를 한 문장으로 설명해 줘."},
    ],
)

print(resp.choices[0].message.content)
print(f"\n사용 토큰: 입력 {resp.usage.prompt_tokens} / 출력 {resp.usage.completion_tokens}")
