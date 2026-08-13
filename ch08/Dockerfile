# 한빛제조 품질 분석 API — 컨테이너 패키징
# 빌드:  docker build -t quality-api .
# 실행:  docker run -p 8000:8000 --env-file .env quality-api
FROM python:3.10-slim

WORKDIR /app

# 의존성을 먼저 복사·설치 — 코드만 바뀌면 이 레이어는 캐시를 재사용한다
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
