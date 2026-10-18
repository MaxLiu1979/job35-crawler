from __future__ import annotations

import json

from ..models import Source
from .base import SourceAdapter, SourceFetch, register

API = "https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true"


@register
class GreenhouseAdapter(SourceAdapter):
    """Greenhouse 公开招聘接口（官方公开 API，无需 key）。"""

    type = "greenhouse"

    def fetch(self, source: Source) -> SourceFetch:
        url = API.format(slug=source.slug)
        raw = self.fetcher.get(url, accept="application/json")
        if not raw:
            return SourceFetch(source_url=url)
        data = json.loads(raw)
        result = SourceFetch(source_url=url)
        for job in data.get("jobs", []):
            result.timestamps.append(job.get("updated_at") or job.get("created_at", ""))
            text = " ".join(
                str(job.get(k, "")) for k in ("title", "location", "content")
            )
            if text.strip():
                result.texts.append(text)
        return result
