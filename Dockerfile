# syntax=docker/dockerfile:1
ARG PYTHON_VERSION=3.14
FROM python:${PYTHON_VERSION}-alpine AS base

# pyc 파일 생성 안 함 / stdout·stderr 버퍼링 끔(로그 즉시 출력)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ARG APP_VERSION=dev
ENV APP_VERSION=${APP_VERSION}

WORKDIR /app

# 비권한 사용자 생성 (컨테이너를 root로 돌리지 않는 보안 best practice)
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# 의존성 먼저 설치 (레이어 캐시 활용). requirements.txt에는 requests, beautifulsoup4만.
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

# su-exec: nologin 계정으로 안전하게 권한 전환하기 위해 (Alpine의 gosu 대체)
RUN apk add --no-cache su-exec

# 소스 복사
COPY . .

RUN chmod +x /app/scripts/docker-entrypoint.sh

ENV CTF_DB_PATH=/app/data/ctf_seen.db

ENTRYPOINT ["/app/scripts/docker-entrypoint.sh"]
CMD ["python", "main.py"]