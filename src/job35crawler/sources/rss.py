from __future__ import annotations

import email.utils
import re
import xml.etree.ElementTree as ET

from ..models import Source
from .base import SourceAdapter, SourceFetch, register

_TAG = re.compile(r"<[^>]+>")


def _text(node: ET.Element | None) -> str:
    if node is None or node.text is None:
        return ""
    return _TAG.sub("", node.text).strip()


@register
class RssAdapter(SourceAdapter):
    """公开招聘 RSS/Atom 源。"""

    type = "rss"

    def fetch(self, source: Source) -> SourceFetch:
        url = source.url or ""
        raw = self.fetcher.get(url)
        if not raw:
            return SourceFetch(source_url=url)
        result = SourceFetch(source_url=url)
        try:
            root = ET.fromstring(raw)
        except ET.ParseError:
            return result
        for item in root.iter():
            if item.tag not in ("item", "{http://www.w3.org/2005/Atom}entry"):
                continue
            title = pub = body = ""
            for child in item:
                local = child.tag.rsplit("}", 1)[-1]
                if local == "title":
                    title = _text(child)
                elif local in ("pubDate", "published", "updated"):
                    pub = (child.text or "").strip()
                elif local in ("description", "summary", "content"):
                    body = _text(child)
            if pub:
                try:
                    dt = email.utils.parsedate_to_datetime(pub)
                    result.timestamps.append(dt.isoformat())
                except (TypeError, ValueError):
                    pass
            text = " ".join(t for t in (title, body) if t)
            if text:
                result.texts.append(text)
        return result
