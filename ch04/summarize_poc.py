# -*- coding: utf-8 -*-
"""첫 PoC: 회의록을 읽어 핵심만 요약한다.

고객(한빛제조, 가상)의 요구: "회의록이 쌓이기만 하고 아무도 안 읽어요.
지난주에 무슨 결정이 있었는지 한눈에 보고 싶어요."

OpenAI API 키가 필요합니다 (.env 파일, 03-2 참조).
실행:  python summarize_poc.py data/회의록_0706_주간품질회의.txt
"""
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()
if not os.getenv("OPENAI_API_KEY"):
    sys.exit("OPENAI_API_KEY가 없습니다. .env 파일을 확인하세요. (03-2 참조)")

client = OpenAI()

PROMPT = """다음 회의록에서 아래 3가지를 뽑아 주세요.

1. 결정 사항 (무엇을 하기로 했나)
2. 할 일 (누가, 언제까지)
3. 리스크 (진행을 막을 수 있는 것)

회의록:
{text}"""


def summarize(path: str) -> str:
    text = Path(path).read_text(encoding="utf-8")
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": PROMPT.format(text=text)}],
        temperature=0,
    )
    return resp.choices[0].message.content


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "data/회의록_0706_주간품질회의.txt"
    print(f"=== {Path(path).name} 요약 ===\n")
    print(summarize(path))
