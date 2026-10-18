from __future__ import annotations

import datetime

from ..models import Activity

ACTIVE_DAYS = 180


def _parse(ts: str) -> datetime.datetime | None:
    ts = ts.strip()
    if not ts:
        return None
    try:
        return datetime.datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        pass
    for fmt in ("%Y-%m-%d", "%Y/%m/%d"):
        try:
            return datetime.datetime.strptime(ts, fmt)
        except ValueError:
            continue
    return None


def judge_activity(timestamps: list[str], today: datetime.date | None = None) -> Activity:
    """根据时间戳判断近 180 天活跃度。

    - 无任何时间戳 → unknown（不猜测）
    - 有合法时间戳 → 最近一次是否落在窗口内
    """
    today = today or datetime.date.today()
    parsed = [d for ts in timestamps if (d := _parse(ts)) is not None]
    if not parsed:
        return Activity(active=None)
    latest = max(parsed)
    last_seen = latest.date().isoformat()
    try:
        active = (today - latest.date()).days <= ACTIVE_DAYS
    except TypeError:
        # 混合了带时区与不带时区的时间：统一按 naive 处理
        latest_naive = latest.replace(tzinfo=None)
        active = (today - latest_naive.date()).days <= ACTIVE_DAYS
        last_seen = latest_naive.date().isoformat()
    return Activity(active=active, last_seen=last_seen)
