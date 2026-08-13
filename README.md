# FDE 따라하기 — 예제 코드

위키독스 책 [「FDE(Forward Deployed Engineer) 따라하기」](https://wikidocs.net/book/20918)의 실습 예제 코드 저장소입니다.

## 구성

| 폴더 | 내용 | 책 |
|---|---|---|
| `ch03/` | 첫 LLM API 호출, .env 예시 | 03장 실습 환경 준비 |
| `ch04/` | 회의록 요약 PoC (단건·일괄) | 04장 첫 프로젝트 |
| `ch05/` | 지저분한 CSV 프로파일링·정제·ETL 파이프라인 | 05장 데이터 파이프라인 |
| `ch06/` | 문서 청킹, BM25/임베딩 검색, QA 챗봇, 검색 품질 평가 | 06장 RAG |
| `ch07/` | 도구 호출 에이전트(모의/실제), 온톨로지 | 07장 AI 에이전트 |
| `ch08/` | FastAPI 서비스, 테스트, Dockerfile | 08장 배포와 내재화 |
| `ch09/` | 실전 프로젝트 2종 (품질 리포트 자동화, 상담 로그 분석) | 09장 실전 프로젝트 |

## 실행 준비

```bash
git clone https://github.com/ady95/fde-tutorial.git
cd fde-tutorial

# uv로 가상환경 + 패키지 설치 (책 03-1 참조)
uv venv .venv
uv pip install pandas rank-bm25 fastapi "uvicorn[standard]" openai python-dotenv tabulate numpy
```

LLM 호출 실습(ch03 일부, ch04, ch06 일부, ch07 일부)은 OpenAI API 키가 필요합니다.
`ch03/.env.example`을 각 장 폴더에 `.env`로 복사하고 키를 넣으세요. (책 03-2 참조)

## 주의

- 등장하는 회사(한빛제조, 하늘상점)와 데이터는 모두 **가상**입니다.
- 실습 데이터의 '지저분함'(인코딩, 표기 불일치, 결측)은 학습을 위해 일부러 넣은 것입니다.
- `.env`(API 키)는 절대 커밋하지 마세요.

## 라이선스

MIT License — 자유롭게 활용하되, 책과 함께 보시면 가장 좋습니다.
