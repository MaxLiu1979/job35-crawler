from __future__ import annotations

import argparse
import json

from .fetcher import PoliteFetcher
from .models import Source
from .pipeline import export, load_companies, run
from .sources import ADAPTERS


def main() -> None:
    parser = argparse.ArgumentParser(prog="job35", description="合规的公开招聘信号采集框架")
    sub = parser.add_subparsers(dest="command", required=True)

    p_run = sub.add_parser("run", help="按企业清单批量采集与分析")
    p_run.add_argument("--companies", required=True, help="companies.yaml 路径")
    p_run.add_argument("--out", default="out", help="输出目录")

    p_check = sub.add_parser("check", help="检查单个来源（调试用）")
    p_check.add_argument("--type", required=True, choices=sorted(ADAPTERS))
    p_check.add_argument("--url")
    p_check.add_argument("--slug")

    args = parser.parse_args()

    if args.command == "run":
        companies = load_companies(args.companies)
        results = run(companies)
        export(results, args.out)
        print(f"完成：{len(results)} 家企业，结果已写入 {args.out}/")
    elif args.command == "check":
        source = Source(type=args.type, url=args.url, slug=args.slug)
        fetched = ADAPTERS[args.type](PoliteFetcher()).fetch(source)
        print(json.dumps(fetched.__dict__, ensure_ascii=False, indent=2))
