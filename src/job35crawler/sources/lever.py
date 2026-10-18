from __future__ import annotations

import datetime
import json

from ..models import Source
from .base import SourceAdapter, SourceFetch, register

API = "https://api.lever.co/v0/postings/{slug}?mode=json"


@register
class LeverAdapter(SourceAdapter):
    """Lever 公开招聘接口（官方公开 API，无需 key）。"""

    type = "lever"

    def fetch(self, source: Source) -> SourceFetch:
        url = API.format(slug=source.slug)
        raw = self.fetcher.get(url, accept="application/json")
        if not raw:
            return SourceFetch(source_url=url)
        postings = json.loads(raw)
        result = SourceFetch(source_url=url)
        for posting in postings:
            ts = posting.get("updatedAt") or posting.get("createdAt")
            if ts:
                dt = datetime.datetime.fromtimestamp(ts / 1000, tz=datetime.timezone.utc)
                result.timestamps.append(dt.isoformat())
            text = " ".join(
                str(posting.get(k, "")) for k in ("text", "description", "additional")
            )
            if text.strip():
                result.texts.append(text)
        return result
