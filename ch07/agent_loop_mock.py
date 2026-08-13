# -*- coding: utf-8 -*-
"""실습 1: 에이전트 루프의 뼈대 — LLM 없이 구조부터 이해한다.

에이전트 = "생각(어떤 도구를 쓸까) -> 행동(도구 호출) -> 관찰(결과 확인)"의 반복.
이 파일은 LLM 대신 '대본(scripted) 두뇌'를 써서 루프 구조만 보여줍니다.
API 키 없이 실행되고, 루프의 동작 원리가 눈에 보입니다.

실행:  python agent_loop_mock.py
"""
import json
import sys

from tools import TOOL_FUNCTIONS, NEEDS_APPROVAL

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


class ScriptedBrain:
    """LLM 흉내: 미리 짜인 판단 순서를 따라간다.

    실제 에이전트에서는 이 부분이 LLM 호출로 바뀝니다 (agent_loop.py).
    """

    def __init__(self):
        self.step = 0

    def decide(self, task: str, observations: list) -> dict:
        plan = [
            {"thought": "먼저 이번 주 불량률을 계산해 보자",
             "tool": "calc_defect_rate",
             "args": {"start_date": "2026-07-06", "end_date": "2026-07-11"}},
            {"thought": "불량률이 가장 높은 라인의 상세 데이터를 보자",
             "tool": "query_quality",
             "args": {"start_date": "2026-07-06", "end_date": "2026-07-11",
                      "line": "B"}},
            {"thought": "분석이 끝났다. 품질팀장에게 리포트를 보내자",
             "tool": "send_report",
             "args": {"recipient": "quality-lead@example.com",
                      "subject": "주간 품질 리포트 (7/6~7/11)",
                      "body": "B라인 불량률이 가장 높습니다. 상세 데이터 첨부."}},
            {"thought": "리포트 발송까지 완료. 작업 종료",
             "tool": None, "args": None},
        ]
        decision = plan[min(self.step, len(plan) - 1)]
        self.step += 1
        return decision


def run_agent(task: str, max_steps: int = 5):
    brain = ScriptedBrain()
    observations = []
    print(f"과업: {task}\n")

    for step in range(1, max_steps + 1):
        decision = brain.decide(task, observations)
        print(f"[{step}] 생각: {decision['thought']}")

        if decision["tool"] is None:          # 도구 호출이 없으면 종료
            print("    => 과업 완료")
            break

        tool_name, args = decision["tool"], decision["args"]
        print(f"    행동: {tool_name}({json.dumps(args, ensure_ascii=False)[:60]}...)")

        # 안전장치: 위험한 도구는 사람에게 승인을 받는다 (HITL)
        if tool_name in NEEDS_APPROVAL:
            ok = input("    이 행동을 실행할까요? (y/n) > ").strip().lower()
            if ok != "y":
                print("    => 사용자가 거부 — 행동 건너뜀")
                observations.append("사용자가 발송을 거부했다")
                continue

        result = TOOL_FUNCTIONS[tool_name](**args)
        observations.append(result)
        print(f"    관찰: {result[:100]}...\n")


if __name__ == "__main__":
    run_agent("지난주 품질 데이터를 분석해서 품질팀장에게 리포트를 보내줘")
