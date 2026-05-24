import hashlib
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Event:
    """CTFtime events API 응답 1건."""
    id: int
    title: str
    ctftime_url: str
    description: str
    logo: str
    weight: float
    onsite: bool
    fmt: str
    restrictions: str
    start_raw: str
    finish_raw: str

    @classmethod
    def from_api(cls, raw: dict) -> Event:
        """API dict -> Event. 누락 필드는 안전한 기본값으로 매핑."""
        return cls(
            id=raw["id"],
            title=raw.get("title", "(제목 없음)"),
            ctftime_url=raw.get("ctftime_url", ""),
            description=raw.get("description", ""),
            logo=raw.get("logo", ""),
            weight=raw.get("weight", 0) or 0,
            onsite=bool(raw.get("onsite")),
            fmt=raw.get("format", "—"),
            restrictions=raw.get("restrictions") or "Open",
            start_raw=raw["start"],
            finish_raw=raw["finish"],
        )

    @property
    def start(self) -> datetime:
        return datetime.fromisoformat(self.start_raw)

    @property
    def finish(self) -> datetime:
        return datetime.fromisoformat(self.finish_raw)

    @property
    def start_ts(self) -> int:
        return int(self.start.timestamp())

    @property
    def duration_text(self) -> str:
        hours = (self.finish - self.start).total_seconds() / 3600
        return f"{hours / 24:.0f}일" if hours >= 48 else f"{hours:.0f}시간"

    @property
    def fingerprint(self) -> str:
        identity = str(self.id)
        return hashlib.sha256(identity.encode()).hexdigest()

    def __str__(self) -> str:
        return f"{self.title} ({self.start_raw}) — {self.ctftime_url}"