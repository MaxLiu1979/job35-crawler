from __future__ import annotations

import datetime
import json
from pathlib import Path

import yaml

from .analyze import judge_activity, judge_age_friendliness
from .fetcher import PoliteFetcher
from .models import Company, CompanyResult
from .sources import ADAPTERS


def load_companies(path: str | Path) -> list[Company]:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return [Company.from_dict(c) for c in data.get("companies", [])]


def run(companies: list[Company], fetcher: PoliteFetcher | None = None) -> list[CompanyResult]:
    fetcher = fetcher or PoliteFetcher()
    results: list[CompanyResult] = []
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    for company in companies:
        all_ts: list[str] = []
        all_texts: list[str] = []
        source_urls: list[str] = []
        for source in company.sources:
            adapter_cls = ADAPTERS.get(source.type)
            if adapter_cls is None:
                continue
            try:
                fetched = adapter_cls(fetcher).fetch(source)
            except Exception as exc:  # 单点失败不拖垮整轮
                print(f"[warn] {company.id} / {source.type}: {exc}")
                continue
            all_ts.extend(fetched.timestamps)
            all_texts.extend(fetched.texts)
            source_urls.append(fetched.source_url)
        url = source_urls[0] if source_urls else ""
        results.append(
            CompanyResult(
                company=company,
                activity=judge_activity(all_ts),
                age=judge_age_friendliness(all_texts, url, now),
            )
        )
    return results


def export(results: list[CompanyResult], out_dir: str | Path) -> None:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    payload = [
        {
            "id": r.company.id,
            "name": r.company.name,
            "industry": r.company.industry,
            "tier": r.company.tier,
            "activity": {"active": r.activity.active, "last_seen": r.activity.last_seen},
            "age_level": r.age.level,
            "age_score": r.age.score,
            "evidence": [e.__dict__ for e in r.age.evidence],
        }
        for r in results
    ]
    (out / "results.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    lines = ["# job35 采集报告\n", f"生成时间：{datetime.datetime.now().isoformat(timespec='seconds')}\n"]
    by_industry: dict[str, list[CompanyResult]] = {}
    for r in results:
        by_industry.setdefault(r.company.industry, []).append(r)
    for industry in sorted(by_industry):
        lines.append(f"\n## {industry}\n")
        lines.append("| 企业 | 层级 | 活跃(180天) | 最近信号 | 35+友好度 |\n")
        lines.append("|---|---|---|---|---|\n")
        for r in sorted(by_industry[industry], key=lambda x: x.company.tier):
            active = {True: "是", False: "否", None: "未知"}[r.activity.active]
            lines.append(
                f"| {r.company.name} | {r.company.tier} | {active} "
                f"| {r.activity.last_seen or '-'} | {r.age.level} ({r.age.score}) |\n"
            )
    (out / "results.md").write_text("".join(lines), encoding="utf-8")
