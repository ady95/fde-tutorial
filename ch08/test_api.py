# -*- coding: utf-8 -*-
"""API 동작 확인 — 서버를 띄우지 않고 TestClient로 검증한다.

실행:  python test_api.py
"""
import sys

from fastapi.testclient import TestClient

from app import app

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

client = TestClient(app)

# 1) 헬스체크
r = client.get("/health")
print(f"GET /health -> {r.status_code} {r.json()}")

# 2) 정상 조회
r = client.get("/defect-rate", params={"start": "2026-07-06",
                                       "end": "2026-07-11"})
print(f"GET /defect-rate -> {r.status_code} {r.json()}")

# 3) 데이터 없는 기간 -> 404
r = client.get("/defect-rate", params={"start": "2025-01-01",
                                       "end": "2025-01-31"})
print(f"GET /defect-rate(과거) -> {r.status_code} {r.json()}")

# 4) 잘못된 입력 -> 422 (FastAPI가 자동 검증)
r = client.get("/defect-rate", params={"start": "잘못된날짜", "end": "2026-07-11"})
print(f"GET /defect-rate(오타) -> {r.status_code}")

# 5) 요약 API — 키가 없으면 501을 돌려주는지
r = client.post("/summarize", json={"text": "이 텍스트는 요약 테스트용 문장입니다."})
print(f"POST /summarize -> {r.status_code} {r.json()}")
