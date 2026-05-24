from __future__ import annotations

import time

import requests
from bs4 import BeautifulSoup

from dto import Event


class Embed:
    """디스코드 임베드 1개를 표현하고 payload dict로 직렬화한다."""

    def __init__(self, event: Event):
        self.event = event

    @staticmethod
    def _color(weight: float) -> int:
        if weight >= 50:
            return 0xF1C40F  # 금색 (대형 대회)
        if weight >= 25:
            return 0x5865F2  # 블러플
        if weight > 0:
            return 0x2ECC71  # 초록
        return 0x95A5A6  # 회색 (가중치 미정)

    @staticmethod
    def _truncate(text: str, n: int) -> str:
        text = (text or "").strip()
        return text if len(text) <= n else text[: n - 1].rstrip() + "…"

    @staticmethod
    def _clean_desc(text: str) -> str:
        """CTFtime 설명의 HTML 정리. <a>는 디스코드 마크다운 링크, <br>는 줄바꿈으로."""
        soup = BeautifulSoup(text or "", "html.parser")
        for br in soup.find_all("br"):
            br.replace_with("\n")
        for a in soup.find_all("a"):
            href = a.get("href", "")
            a.replace_with(f"[{a.get_text()}]({href})" if href else a.get_text())
        return soup.get_text().strip()

    def to_dict(self) -> dict:
        e = self.event
        place = "Onsite" if e.onsite else "Online"  # 도메인 값이라 원문 유지

        embed = {
            "title": self._truncate(e.title, 256),
            "url": e.ctftime_url,
            "description": self._truncate(self._clean_desc(e.description), 400),
            "color": self._color(e.weight),
            # 레이어 분리: 라벨=한글(읽는 사람 언어), 값=CTFtime 원문(Jeopardy/Open/Onsite).
            # 이모지는 정보를 안 더하는 장식이라 제거 — 색 막대+로고가 시각 앵커.
            # <t:..:R> 상대시간은 디스코드가 보는 사람 로캘로 자동 변환("5일 후"/"in 5 days").
            "fields": [
                {"name": "시작", "value": f"<t:{e.start_ts}:F>\n<t:{e.start_ts}:R>", "inline": True},
                {"name": "기간", "value": e.duration_text, "inline": True},
                {"name": "형식", "value": f"{e.fmt} · {place}", "inline": True},
                {"name": "가중치", "value": f"{e.weight:g}", "inline": True},
                {"name": "참가", "value": e.restrictions, "inline": True},
            ],
            "footer": {"text": f"CTFtime · event #{e.id}"},
        }
        if e.logo:
            embed["thumbnail"] = {"url": e.logo}
        return embed

class DiscordWebhook:
    """임베드 객체들을 받아 디스코드로 전송."""

    def __init__(self, url: str, *, dry_run: bool = False):
        self.url = url
        self.dry_run = dry_run

    def send(self, embeds: list[Embed]) -> None:
        if self.dry_run:
            print(f"[DRY_RUN] 전송 안 함. 새 대회 {len(embeds)}개:")
            for em in embeds:
                print(f"  - {em.event}")
            return
        payloads = [em.to_dict() for em in embeds]
        for i in range(0, len(payloads), 10):     # 메시지당 임베드 최대 10개
            self._post({"embeds": payloads[i : i + 10]})

    def _post(self, payload: dict) -> None:
        while True:
            r = requests.post(self.url, json=payload, timeout=10)
            if r.status_code == 429:               # rate limit
                wait = float(r.json().get("retry_after", 1)) + 0.5
                print(f"  rate limited, {wait:.1f}s 대기...")
                time.sleep(wait)
                continue
            r.raise_for_status()
            return
