# -*- coding: utf-8 -*-
"""실습 1: 데이터 프로파일링 — 손대기 전에 파악한다.

고객 데이터를 받으면 정제부터 시작하지 않습니다.
먼저 '무엇이 문제인지' 목록을 만듭니다. 이 목록이 고객과의 대화 재료가 됩니다.
"""
import sys

import pandas as pd

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# 1) 인코딩: utf-8로 읽으면 UnicodeDecodeError — 현장 CSV는 cp949가 많다
try:
    df = pd.read_csv("data/quality_raw.csv", encoding="utf-8")
except UnicodeDecodeError as e:
    print(f"utf-8 읽기 실패: {e}")
    print("=> cp949로 재시도\n")
    df = pd.read_csv("data/quality_raw.csv", encoding="cp949")

# 2) 기본 형태
print(f"행 x 열: {df.shape[0]} x {df.shape[1]}")
print(f"컬럼명: {list(df.columns)}")   # 공백이 섞였는지 눈으로 확인
print()

# 3) 타입과 결측치
print(df.dtypes.to_string())
print()
print("결측치 개수:")
print(df.isna().sum().to_string())
print()

# 4) 중복 행
print(f"완전 중복 행: {df.duplicated().sum()}건")
print()

# 5) 범주형 컬럼의 표기 흔들림 — 정제 목록의 핵심
for col in ["라인", "판정"]:
    print(f"[{col}] 고유값: {sorted(df[col].dropna().unique().tolist())}")
print()

# 6) 수치여야 하는 컬럼이 문자열인 이유 찾기
col = "측정값(mm)"
non_numeric = df[pd.to_numeric(df[col], errors="coerce").isna() & df[col].notna()]
print(f"[{col}] 숫자로 변환 안 되는 값 {len(non_numeric)}건:")
print(non_numeric[[col]].to_string())
