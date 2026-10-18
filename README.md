# job35-crawler

一个**合规优先**的公开招聘信号采集框架：自动捕捉那些在近半年内招聘仍然活跃、且对 35 岁以上求职者（一线员工与中高管均覆盖）友好的网站与企业。

> 姊妹仓库（名录与数据）：[job35-directory](https://github.com/MaxLiu1979/job35-directory)
>
> English version: [README.en.md](README.en.md)

## 设计原则

1. **合规优先**：只采集公开可访问的数据；遵守 robots.txt；不绕过登录、验证码或任何反爬机制；控制请求频率（默认每域名 2 秒一次）。无法读取 robots.txt 时按**禁止抓取**处理。
2. **公开信号，不碰招聘站内容**：主流招聘平台（LinkedIn、猎聘、BOSS 直聘等）的用户协议禁止爬取，本框架**不包含**针对它们的适配器。数据源限定为：
   - 企业官方招聘页（careers page）
   - 公开 ATS API（Greenhouse、Lever 的公开接口）
   - 企业招聘 RSS / 官方博客公开招聘公告
3. **证据驱动**：每个结论都必须带可核查的公开证据（URL + 原文摘录 + 采集时间），不输出无证据的判断。
4. **活跃度可机器验证**：企业被标记为"活跃"的前提是最近 180 天内存在公开招聘信号；查不到日期时标记为 `unknown`，而不是猜。

## 安装与运行

```bash
pip install -e .
# 或者直接使用源码（仅需 Python 3.10+ 和 pyyaml）

# 对名录仓库中的企业跑一遍采集与分析
job35 run --companies ../job35-directory/data/companies.yaml --out out/

# 对单个企业做检查（调试用）
job35 check --type greenhouse --slug example

# 使用独立配置文件（不依赖名录仓库）
cp config/sources.example.yaml my_sources.yaml
job35 run --companies my_sources.yaml --out out/
```

输出：

- `out/results.json`：结构化结果（活跃度 + 35+ 友好度评分 + 证据）
- `out/results.md`：按行业汇总的人类可读报告

## 数据来源类型（适配器）

| type | 说明 | 是否需要 key |
|---|---|---|
| `greenhouse` | Greenhouse 公开招聘接口 `boards-api.greenhouse.io` | 否 |
| `lever` | Lever 公开招聘接口 `api.lever.co` | 否 |
| `careers_page` | 企业官网招聘页 HTML，提取职位发布日期 | 否 |
| `rss` | 公开招聘 RSS/Atom 源 | 否 |

新增适配器：在 `src/job35crawler/sources/` 下继承 `base.SourceAdapter` 并在 `base.ADAPTERS` 注册。欢迎 PR（新适配器同样必须遵守上述合规原则）。

## 35+ 友好度判定方法（摘要）

对采集到的公开文本按关键词分级打分，完整定义见
[job35-directory/docs/methodology.md](https://github.com/MaxLiu1979/job35-directory/blob/main/docs/methodology.md)：

- `explicit`：出现明确欢迎资深/不限年龄的公开表述
- `likely`：长期经验要求（如 10+ 年经验岗）等间接信号
- `unknown`：无可用信号
- `risky`：出现明确年龄上限（如"35 岁以下"）

## 自动化执行

`.github/workflows/crawl.yml` 提供每周定时任务模板：拉取名录仓库 → 运行采集 → 把结果以 PR 形式提回名录仓库。跨仓库推送需要你在仓库 Settings 中配置 PAT（详见 workflow 内注释），也可以先让它只上传 artifact。

## 免责声明

本框架只做**公开信息的聚合与标注**，所有结论以原始公开页面为准，不构成任何求职建议。若某企业认为标注有误，请在名录仓库提交 issue 并附公开证据，核实后会更正。

## License

MIT（代码）。数据名录仓库使用 CC0-1.0，见 job35-directory。
