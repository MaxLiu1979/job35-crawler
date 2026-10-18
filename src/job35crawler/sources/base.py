from __future__ import annotations

from dataclasses import dataclass, field

from ..fetcher import PoliteFetcher
from ..models import Source


@dataclass
class SourceFetch:
    """一次来源采集的原始结果。"""

    source_url: str
    texts: list[str] = field(default_factory=list)          # 供年龄友好度分析的文本
    timestamps: list[str] = field(default_factory=list)     # ISO 时间，供活跃度判断


class SourceAdapter:
    type: str = ""

    def __init__(self, fetcher: PoliteFetcher) -> None:
        self.fetcher = fetcher

    def fetch(self, source: Source) -> SourceFetch:  # pragma: no cover
        raise NotImplementedError


ADAPTERS: dict[str, type[SourceAdapter]] = {}


def register(cls: type[SourceAdapter]) -> type[SourceAdapter]:
    ADAPTERS[cls.type] = cls
    return cls


from . import careers_page, greenhouse, lever, rss  # noqa: E402,F401
