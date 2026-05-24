# kctf_webhook_notification

[CTFtime](https://ctftime.org/)에 등록된 다가오는 CTF 대회를 주기적으로 조회해 디스코드 채널에 임베드 메시지로 알려주는 봇입니다.

---

## 기능

- CTFtime API에서 N일 이내에 시작하는 대회 목록을 가져옴
- 대회별로 가중치/형식/일정/참가 조건 등을 포함한 디스코드 임베드 생성
- 가중치에 따라 임베드 색상 차등 (50+ 금색, 25+ 블러플, 0+ 초록, 미정 회색)
- SQLite로 중복 발송 방지
- 지정 주기로 데몬처럼 동작 가능

---

## 환경변수

### 필수

| 이름 | 설명 |
| --- | --- |
| `DISCORD_WEBHOOK_URL` | 대회 알림을 받을 디스코드 채널의 웹훅 URL. 비어 있으면 시작 시 즉시 종료. |

### 선택

| 이름 | 기본값 | 설명 |
| --- | --- | --- |
| `DAYS_AHEAD` | `7` | 지금 시각부터 며칠 이내에 시작하는 대회까지 조회할지. |
| `MAX_EVENTS` | `20` | CTFtime API에서 한 번에 가져올 최대 대회 수. |
| `INTERVAL` | `0` | 폴링 주기(초). `0`이면 한 번만 실행 후 종료. 데몬으로 돌리려면 `3600` 등 양수 지정. |
| `CTF_DB_PATH` | `./ctf_seen.db` (Docker: `/app/data/ctf_seen.db`) | 전송 이력을 저장할 SQLite 파일 경로. 부모 디렉터리는 자동 생성됨. |

> Docker 이미지에서는 `CTF_DB_PATH=/app/data/ctf_seen.db`로 이미 설정되어 있으므로 `/app/data`를 볼륨 마운트하면 컨테이너를 재시작해도 이력이 유지됩니다.

## 로컬 실행

요구사항: Python 3.14 이상.

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/xxx/yyy"
python main.py
```

---

## Docker로 실행

### 미리 빌드된 이미지 사용

```bash
docker pull ghcr.io/jjh4450/kctf_webhook_notification:latest

docker run --rm \
  -e DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/xxx/yyy" \
  -v $(pwd)/data:/app/data \
  ghcr.io/jjh4450/kctf_webhook_notification:latest
```

사용 가능한 태그:

- `latest` : `main` 브랜치에 push될 때마다 갱신
- `triweekly` : 3주에 한 번 자동 빌드되는 태그 (권장)
- `vYYYY.MM.DD-<sha>` : 빌드별 고정 태그 (GitHub Release와 1:1 대응)

### 로컬에서 직접 빌드

```bash
docker build -t kctf-webhook .
docker run --rm \
  -e DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/xxx/yyy" \
  -v $(pwd)/data:/app/data \
  kctf-webhook
```
---

## 프로젝트 구조

```
.
├── main.py                       # 진입점. 폴링 루프 / 단발 실행 분기
├── config.py                     # 환경변수 로드
├── dto.py                        # Event DTO (CTFtime API 응답 1건)
├── discord.py                    # Embed 직렬화 + Webhook 송신
├── store.py                      # SQLite SeenStore (중복 발송 방지)
├── requirements.txt
├── Dockerfile                    # Alpine 기반 멀티 아키 이미지
├── scripts/docker-entrypoint.sh  # 볼륨 권한 처리 + su-exec drop-privilege
└── .github/workflows/docker-build.yml
```

---


문의: jjh4450git@gmail.com
