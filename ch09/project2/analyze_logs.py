# -*- coding: utf-8 -*-
"""프로젝트 2 (1단계): 상담 로그 정제와 분류.

고객 요구(하늘상점, 가상): "상담이 뭐가 많이 들어오는지 모르겠어요.
카테고리를 상담원마다 다르게 적어서 통계를 못 내요."

전략: LLM을 부르기 전에 규칙 기반 분류로 기준선을 잡는다.
규칙으로 80%가 잡히면, 나머지 20%만 LLM에 맡기면 된다 (비용 절약).

실행:  python analyze_logs.py
"""
import sys

import pandas as pd

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# 표기 통일: 상담원 제각각 표기 -> 표준 카테고리
CATEGORY_MAP = {
    "배송": "배송", "배송문의": "배송", "delivery": "배송",
    "환불": "환불", "환불문의": "환불",
    "교환": "교환", "교환문의": "교환",
    "회원": "회원", "회원문의": "회원",
    "결제": "결제", "상품": "상품", "상품문의": "상품",
}

# 카테고리가 빈 로그를 위한 키워드 규칙 (우선순위 순서대로 검사)
KEYWORD_RULES = [
    ("환불", ["환불", "반품", "취소"]),
    ("교환", ["교환", "불량"]),
    ("배송", ["배송", "송장", "출고", "도착"]),
    ("결제", ["결제", "입금", "카드", "쿠폰", "포인트"]),
    ("회원", ["비밀번호", "아이디", "탈퇴", "계정"]),
    ("상품", ["재입고", "세탁", "사이즈"]),
]


def classify(text: str) -> str:
    for category, keywords in KEYWORD_RULES:
        if any(k in text for k in keywords):
            return category
    return "기타"


df = pd.read_csv("data/consult_logs.csv")
total = len(df)

# 1) 기존 카테고리 표기 통일
df["카테고리"] = df["카테고리"].map(CATEGORY_MAP)

# 2) 비어 있는 카테고리는 키워드 규칙으로 채움
empty = df["카테고리"].isna()
df.loc[empty, "카테고리"] = df.loc[empty, "문의내용"].map(classify)
print(f"전체 {total}건 중 카테고리 누락 {empty.sum()}건 -> 규칙으로 분류")

# 3) 통계
print("\n카테고리별 문의량:")
print(df["카테고리"].value_counts().to_string())
print("\n채널별 문의량:")
print(df["채널"].value_counts().to_string())

df.to_csv("data/consult_logs_labeled.csv", index=False, encoding="utf-8-sig")
print("\ndata/consult_logs_labeled.csv 저장 완료")
