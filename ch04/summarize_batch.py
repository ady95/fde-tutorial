# -*- coding: utf-8 -*-
"""PoC 확장: 폴더의 회의록 전체를 일괄 요약해 하나의 주간 브리핑으로 만든다.

실행:  python summarize_batch.py data
결과:  weekly_briefing.md
"""
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from summarize_poc import summarize

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()
if not os.getenv("OPENAI_API_KEY"):
    sys.exit("OPENAI_API_KEY가 없습니다. .env 파일을 확인하세요. (03-2 참조)")

client = OpenAI()

folder = Path(sys.argv[1] if len(sys.argv) > 1 else "data")
files = sorted(folder.glob("*.txt"))
print(f"회의록 {len(files)}건 요약 시작")

sections = []
for path in files:
    print(f"  - {path.name}")
    sections.append(f"### {path.stem}\n\n{summarize(path)}")

# 개별 요약을 모아 한 번 더 종합 — 요약의 요약
resp = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user",
               "content": "다음 회의 요약들을 종합해서 '이번 주 핵심 3줄'을 "
                          "만들어 주세요:\n\n" + "\n\n".join(sections)}],
    temperature=0,
)

briefing = (f"## 주간 브리핑\n\n{resp.choices[0].message.content}\n\n---\n\n"
            + "\n\n".join(sections))
Path("weekly_briefing.md").write_text(briefing, encoding="utf-8")
print("\nweekly_briefing.md 생성 완료")
