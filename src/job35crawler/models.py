from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Source:
    """一个可采集的公开招聘信号来源。"""

    type: str                     # greenhouse | lever | careers_page | rss
    url: str | None = None
    slug: str | None = None
    note: str | None = None


@dataclass
class Company:
    id: str
    name: str
    industry: str
    tier: str = "candidate"       # top10 | top50 | top100 | candidate
    country: str | None = None
    name_en: str | None = None
    sources: list[Source] = field(default_factory=list)
    status: str = "pending"       # pending | active | verified | stale
    note: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Company":
        sources = [Source(**s) for s in data.get("sources", [])]
        return cls(
            id=data["id"],
            name=data["name"],
            industry=data["industry"],
            tier=data.get("tier", "candidate"),
            country=data.get("country"),
            name_en=data.get("name_en"),
            sources=sources,
            status=data.get("status", "pending"),
            note=data.get("note"),
        )


@dataclass
class Evidence:
    source_url: str
    signal: str                   # 命中了什么信号
    quote: str                    # 原文摘录（截取，保留上下文）
    captured_at: str              # ISO 时间


@dataclass
class AgeVerdict:
    level: str                    # explicit | likely | unknown | risky
    score: int
    evidence: list[Evidence] = field(default_factory=list)


@dataclass
class Activity:
    active: bool | None           # True=180天内有信号 False=能确认无信号 None=unknown
    last_seen: str | None = None  # ISO 日期


@dataclass
class CompanyResult:
    company: Company
    activity: Activity
    age: AgeVerdict
