from __future__ import annotations

from ..models import AgeVerdict, Evidence

# 明确欢迎 35+ / 不限年龄的公开表述（+2 分）
FRIENDLY = [
    "不限年龄", "年龄不限", "欢迎资深", "资深人才", "重返职场", "再就业",
    "age no bar", "regardless of age", "no age limit", "open to all ages",
    "age-friendly", "age friendly", "returnship", "return to work program",
    "career restarter", "experienced professionals welcome", "second career",
]

# 间接信号：长期经验要求，暗示欢迎资深从业者（+1 分）
EXPERIENCED = [
    "10年以上", "十年以上", "8年以上", "五年以上", "资深",
    "10+ years", "8+ years", "5+ years", "senior professional", "seasoned",
]

# 明确年龄上限（一旦出现直接判 risky）
RISKY = [
    "35岁以下", "35 岁以下", "35周岁以下", "35 周岁以下", "年龄35以下",
    "30岁以下", "28岁以下",
    "under 35", "below 35", "under 30", "aged under",
]

QUOTE_LEN = 80


def _find(texts: list[str], keywords: list[str]) -> list[tuple[str, str]]:
    """返回 (关键词, 上下文摘录) 列表。"""
    hits = []
    joined = "\n".join(texts).lower()
    for kw in keywords:
        low = kw.lower()
        idx = joined.find(low)
        if idx != -1:
            start = max(0, idx - 30)
            quote = joined[start:idx + len(low) + QUOTE_LEN].replace("\n", " ")
            hits.append((kw, f"…{quote}…"))
    return hits


def judge_age_friendliness(texts: list[str], source_url: str, captured_at: str) -> AgeVerdict:
    risky = _find(texts, RISKY)
    friendly = _find(texts, FRIENDLY)
    experienced = _find(texts, EXPERIENCED)

    evidence = [
        Evidence(source_url=source_url, signal=f"age_cap:{kw}", quote=q, captured_at=captured_at)
        for kw, q in risky
    ]
    evidence += [
        Evidence(source_url=source_url, signal=f"friendly:{kw}", quote=q, captured_at=captured_at)
        for kw, q in friendly
    ]
    evidence += [
        Evidence(source_url=source_url, signal=f"experienced:{kw}", quote=q, captured_at=captured_at)
        for kw, q in experienced
    ]

    if risky:
        return AgeVerdict(level="risky", score=-3 * len(risky), evidence=evidence)
    if friendly:
        return AgeVerdict(level="explicit", score=2 * len(friendly) + len(experienced), evidence=evidence)
    if experienced:
        return AgeVerdict(level="likely", score=len(experienced), evidence=evidence)
    return AgeVerdict(level="unknown", score=0, evidence=evidence)
