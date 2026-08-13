# -*- coding: utf-8 -*-
"""실습 1: 문서 청킹 — 검색의 단위를 만든다.

문서 전체를 통째로 검색하면 정확도가 떨어집니다.
'## 소제목' 단위로 잘라서, 하나의 청크가 하나의 주제만 담게 합니다.
결과는 chunks.json으로 저장해 검색 실습에서 재사용합니다.
"""
import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

DOCS_DIR = Path("data/docs")


def chunk_by_heading(text: str, source: str) -> list[dict]:
    """'## 소제목' 단위로 문서를 자른다. 문서 제목은 모든 청크에 함께 담는다."""
    title_match = re.match(r"#\s+(.+)", text)
    doc_title = title_match.group(1).strip() if title_match else source

    chunks = []
    for m in re.split(r"(?=^## )", text, flags=re.MULTILINE):
        if not m.strip().startswith("## "):
            continue
        heading = m.splitlines()[0].replace("## ", "").strip()
        body = "\n".join(m.splitlines()[1:]).strip()
        chunks.append({
            "id": f"{source}#{heading}",
            "doc_title": doc_title,
            "heading": heading,
            "text": body,
        })
    return chunks


all_chunks = []
for path in sorted(DOCS_DIR.glob("*.md")):
    text = path.read_text(encoding="utf-8")
    chunks = chunk_by_heading(text, path.stem)
    all_chunks.extend(chunks)
    print(f"{path.name}: 청크 {len(chunks)}개")

Path("chunks.json").write_text(
    json.dumps(all_chunks, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n총 {len(all_chunks)}개 청크 -> chunks.json")
print(f"\n청크 예시:\n{json.dumps(all_chunks[0], ensure_ascii=False, indent=2)}")
