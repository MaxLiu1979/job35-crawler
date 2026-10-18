# job35-crawler

A **compliance-first** framework for collecting public hiring signals: it automatically surfaces companies and sites whose recruiting has been active in the last 6 months and that are friendly to job seekers aged 35+ (both individual contributors and executives).

> Sister repo (directory & data): [job35-directory](https://github.com/MaxLiu1979/job35-directory)
>
> 中文版：[README.md](README.md)

## Design principles

1. **Compliance first.** Public data only; honors robots.txt; never bypasses login, CAPTCHA, or any anti-bot mechanism; rate-limits requests (2s per domain by default). If robots.txt cannot be fetched, crawling is treated as **disallowed**.
2. **Public signals, not job-board scraping.** Major job platforms (LinkedIn, Liepin, BOSS Zhipin, …) prohibit crawling in their ToS and are **deliberately out of scope**. Data sources are limited to:
   - Company official careers pages
   - Public ATS APIs (Greenhouse, Lever)
   - Public recruiting RSS feeds / official hiring announcements
3. **Evidence-driven.** Every conclusion must carry verifiable public evidence (URL + quote + captured time).
4. **Machine-checkable freshness.** A company is marked `active` only when a public hiring signal exists within the last 180 days; when no date is found, it is marked `unknown`, never guessed.

## Install & run

```bash
pip install -e .

# Run collection + analysis over the directory repo
job35 run --companies ../job35-directory/data/companies.yaml --out out/

# Check a single source (debugging)
job35 check --type greenhouse --slug example

# Standalone config (no directory repo needed)
cp config/sources.example.yaml my_sources.yaml
job35 run --companies my_sources.yaml --out out/
```

Outputs:

- `out/results.json` — structured results (activity + 35+ friendliness level + evidence)
- `out/results.md` — human-readable summary grouped by industry

## Source types (adapters)

| type | description | key required |
|---|---|---|
| `greenhouse` | Greenhouse public boards API | no |
| `lever` | Lever public postings API | no |
| `careers_page` | Company careers page HTML, extracting posting dates | no |
| `rss` | Public recruiting RSS/Atom feed | no |

To add an adapter, subclass `base.SourceAdapter` in `src/job35crawler/sources/` and register it in `base.ADAPTERS`. PRs welcome — new adapters must follow the compliance principles above.

## How the 35+ friendliness level is scored (summary)

Keyword-based grading over collected public text. Full definition:
[job35-directory/docs/methodology.md](https://github.com/MaxLiu1979/job35-directory/blob/main/docs/methodology.md)

- `explicit` — explicit public statements welcoming senior talent / no age limit
- `likely` — indirect signals such as long-experience requirements (10+ years)
- `unknown` — no usable signal
- `risky` — explicit age caps (e.g. "under 35")

## Automation

`.github/workflows/crawl.yml` is a weekly cron template: pull the directory repo, run the crawl, and open a PR back to the directory repo with updated results. Cross-repo push requires a PAT configured in repo Settings (see comments in the workflow); it can also just upload artifacts instead.

## Disclaimer

This framework only aggregates and labels **publicly available information**. All conclusions should be verified against the original pages and do not constitute career advice. If a company believes a label is wrong, open an issue in the directory repo with public evidence and it will be corrected.

## License

MIT (code). The directory repo's data is CC0-1.0, see job35-directory.
