#!/usr/bin/env python3
"""CTFtime 다가오는 대회 -> 디스코드 임베드 알림.

구조:
  - Event        : API 응답 1건을 담는 DTO (parse_dt / ts 를 property로 내부화)
  - Embed        : 디스코드 임베드 1개를 표현/직렬화하는 객체
  - SeenStore    : 이미 보낸 대회의 해시를 SQLite에 보관 (with 문 지원)
  - DiscordWebhook : 송신 담당 객체
"""

from __future__ import annotations

import time

import requests

from config import (
    CTFTIME_API,
    DB_PATH,
    DAYS_AHEAD,
    INTERVAL,
    MAX_EVENTS,
    USER_AGENT,
    WEBHOOK_URL,
    DRY_RUN,
)
from discord import DiscordWebhook, Embed
from dto import Event
from store import SeenStore


def fetch_events() -> list[Event]:
    now = int(time.time())
    resp = requests.get(
        CTFTIME_API,
        params={"limit": MAX_EVENTS, "start": now, "finish": now + DAYS_AHEAD * 86400},
        headers={"User-Agent": USER_AGENT},
        timeout=10,
    )
    resp.raise_for_status()
    return [Event.from_api(raw) for raw in resp.json()]


def run_once() -> None:
    events = fetch_events()
    webhook = DiscordWebhook(WEBHOOK_URL, dry_run=DRY_RUN)

    with SeenStore(DB_PATH) as store:
        new_events = [e for e in events if store.is_new(e)]
        if not new_events:
            print("새로 보낼 대회가 없어요. (전부 이미 보냈거나 예정 대회 없음)")
            return

        embeds = [Embed(e) for e in new_events]
        webhook.send(embeds)

        if not DRY_RUN:
            store.mark_sent(new_events)            # 전송 성공 후에만 기록
            print(f"새 대회 {len(new_events)}개 전송 완료.")


def main() -> None:
    if not DRY_RUN and not WEBHOOK_URL:
        raise SystemExit("DISCORD_WEBHOOK_URL 환경변수가 비어 있습니다.")

    if INTERVAL <= 0:
        run_once()
        return

    while True:
        try:
            run_once()
        except Exception as exc:
            print(f"이번 주기 실패: {exc!r}")
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()