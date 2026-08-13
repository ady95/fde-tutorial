# -*- coding: utf-8 -*-
"""실습 2: 진짜 에이전트 — 대본을 LLM으로 교체한다.

agent_loop_mock.py와 루프 구조는 완전히 같습니다.
'다음에 무엇을 할지'를 대본이 아니라 LLM이 결정한다는 점만 다릅니다.

OpenAI API 키가 필요합니다 (.env 파일 또는 환경변수 OPENAI_API_KEY).
실행:  python agent_loop.py "지난주 품질 데이터를 분석해서 리포트를 보내줘"
"""
import json
import os
import sys

from dotenv import load_dotenv
from openai import OpenAI

from tools import TOOL_FUNCTIONS, TOOL_SPECS, NEEDS_APPROVAL

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()
if not os.getenv("OPENAI_API_KEY"):
    sys.exit("OPENAI_API_KEY가 없습니다. .env 파일을 확인하세요. (03-2 참조)")

client = OpenAI()
MODEL = "gpt-4o-mini"

SYSTEM_PROMPT = """당신은 한빛제조(가상 회사)의 품질 분석 에이전트입니다.
도구를 사용해 데이터를 조회·분석하고, 요청받은 작업을 완료하세요.
오늘은 2026-07-13(월)이고, '지난주'는 2026-07-06 ~ 2026-07-11입니다.
분석 없이 추측으로 답하지 마세요."""


def run_agent(task: str, max_steps: int = 8):
    messages = [{"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": task}]
    print(f"과업: {task}\n")

    for step in range(1, max_steps + 1):
        resp = client.chat.completions.create(
            model=MODEL, messages=messages, tools=TOOL_SPECS)
        msg = resp.choices[0].message
        messages.append(msg)

        if not msg.tool_calls:               # 도구 호출이 없으면 최종 답변
            print(f"[{step}] 최종 답변:\n{msg.content}")
            break

        for call in msg.tool_calls:
            name = call.function.name
            args = json.loads(call.function.arguments)
            print(f"[{step}] 행동: {name}({call.function.arguments[:80]})")

            if name in NEEDS_APPROVAL:       # 안전장치 (HITL)
                ok = input("    이 행동을 실행할까요? (y/n) > ").strip().lower()
                if ok != "y":
                    result = json.dumps({"error": "사용자가 거부했습니다"},
                                        ensure_ascii=False)
                    messages.append({"role": "tool",
                                     "tool_call_id": call.id, "content": result})
                    continue

            result = TOOL_FUNCTIONS[name](**args)
            print(f"    관찰: {result[:100]}...\n")
            messages.append({"role": "tool",
                             "tool_call_id": call.id, "content": result})


if __name__ == "__main__":
    task = sys.argv[1] if len(sys.argv) > 1 else (
        "지난주 품질 데이터를 분석해서 요약해 줘. 발송은 하지 마.")
    run_agent(task)
