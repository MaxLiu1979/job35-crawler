from __future__ import annotations

import re

from ..models import Source
from .base import SourceAdapter, SourceFetch, register

DATE_PATTERNS = [
    re.compile(r"(20\d{2})-(\d{1,2})-(\d{1,2})"),
    re.compile(r"(20\d{2})/(\d{1,2})/(\d{1,2})"),
    re.compile(r"(20\d{2})年(\d{1,2})月(\d{1,2})日?"),
]


@register
class CareersPageAdapter(SourceAdapter):
    """企业官网招聘页：保留全文文本供关键词分析，提取页面中出现的日期。"""

    type = "careers_page"

    def fetch(self, source: Source) -> SourceFetch:
        url = source.url or ""
        raw = self.fetcher.get(url)
        if not raw:
            return SourceFetch(source_url=url)
        html = raw.decode("utf-8", errors="replace")
        result = SourceFetch(source_url=url, texts=[html])
        seen: set[str] = set()
        for pattern in DATE_PATTERNS:
            for match in pattern.finditer(html):
                stamp = f"{match.group(1)}-{int(match.group(2)):02d}-{int(match.group(3)):02d}"
                if stamp not in seen:
                    seen.add(stamp)
                    result.timestamps.append(stamp)
        return result
