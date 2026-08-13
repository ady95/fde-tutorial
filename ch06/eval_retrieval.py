# -*- coding: utf-8 -*-
"""실습: 검색 품질 평가 — 감이 아니라 숫자로 말한다.

평가 데이터셋(질문 + 정답 문서)을 만들고 적중률(hit rate)을 측정합니다.
"괜찮아 보이는데요"가 아니라 "적중률 90%입니다"라고 말하는 것이
FDE가 고객의 신뢰를 얻는 방식입니다.
"""
import sys

from bm25_search import search

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# 평가 데이터셋: (질문, 정답 청크가 속한 문서)
# 실제 프로젝트에서는 고객사 담당자와 함께 20~50개를 만듭니다.
EVAL_SET = [
    ("연차는 며칠 전에 신청해야 하나요?", "휴가규정"),
    ("배우자가 출산하면 휴가가 며칠인가요?", "휴가규정"),
    ("여름휴가는 며칠인가요?", "휴가규정"),
    ("법인카드로 30만 원 넘게 쓰려면 어떻게 하나요?", "경비처리지침"),
    ("택시비는 언제 인정되나요?", "경비처리지침"),
    ("간이영수증은 얼마까지 인정되나요?", "경비처리지침"),
    ("재택근무는 주 몇 회까지 가능한가요?", "재택근무규정"),
    ("수습 기간에도 재택근무를 할 수 있나요?", "재택근무규정"),
    ("비밀번호는 얼마나 자주 바꿔야 하나요?", "보안정책"),
    ("회사 자료를 생성형 AI에 넣어도 되나요?", "보안정책"),
    ("해외 출장은 언제까지 신청해야 하나요?", "출장규정"),
    ("고객사에 한 달 넘게 파견 가면 수당이 있나요?", "출장규정"),
    ("노트북은 몇 년마다 바꿔주나요?", "장비신청지침"),
    ("퇴사할 때 장비는 어떻게 하나요?", "장비신청지침"),
    # 말바꿈 질문: 규정의 단어를 쓰지 않고 묻는다 — 키워드 검색의 약점 확인용
    ("집에서 일해도 되나요?", "재택근무규정"),
    ("결혼하면 회사 안 나와도 되는 날이 있나요?", "휴가규정"),
    ("챗GPT에 설계 도면을 올려도 되나요?", "보안정책"),
]


def evaluate(top_k: int) -> float:
    hits = 0
    misses = []
    for question, answer_doc in EVAL_SET:
        results = search(question, top_k=top_k)
        found_docs = [chunk["id"].split("#")[0] for _, chunk in results]
        if answer_doc in found_docs:
            hits += 1
        else:
            misses.append((question, answer_doc, found_docs[0]))
    rate = hits / len(EVAL_SET)
    print(f"적중률@{top_k}: {hits}/{len(EVAL_SET)} = {rate:.0%}")
    for q, expected, got in misses:
        print(f"  빗나감: '{q}' 정답={expected}, 1위={got}")
    return rate


if __name__ == "__main__":
    print(f"평가 질문 {len(EVAL_SET)}개 (BM25 검색)\n")
    evaluate(top_k=1)
    print()
    evaluate(top_k=3)
