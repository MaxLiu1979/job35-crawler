from __future__ import annotations

import time
import urllib.error
import urllib.request
import urllib.robotparser
from urllib.parse import urlparse

USER_AGENT = "job35-crawler/0.1 (+https://github.com/MaxLiu1979/job35-crawler; robots.txt honored, no anti-bot bypass)"


class PoliteFetcher:
    """遵守 robots.txt 与速率限制的抓取器。

    合规要点：
    - 每次请求前检查 robots.txt；读取失败一律视为禁止抓取（保守策略）。
    - 每个域名默认 2 秒一个请求。
    - 永不伪装成浏览器、永不携带登录态。
    """

    def __init__(self, delay_seconds: float = 2.0, timeout: float = 15.0) -> None:
        self.delay = delay_seconds
        self.timeout = timeout
        self._robots: dict[str, urllib.robotparser.RobotFileParser] = {}
        self._last_hit: dict[str, float] = {}

    def _robot(self, url: str) -> urllib.robotparser.RobotFileParser:
        host = urlparse(url).netloc
        if host not in self._robots:
            rp = urllib.robotparser.RobotFileParser()
            rp.set_url(f"{urlparse(url).scheme}://{host}/robots.txt")
            try:
                rp.read()
            except Exception:
                # robots.txt 不可达：按禁止处理，宁可少抓不可越界
                rp.parse(["User-agent: *", "Disallow: /"])
            self._robots[host] = rp
        return self._robots[host]

    def allowed(self, url: str) -> bool:
        return self._robot(url).can_fetch(USER_AGENT, url)

    def _wait(self, url: str) -> None:
        host = urlparse(url).netloc
        elapsed = time.monotonic() - self._last_hit.get(host, 0.0)
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)
        self._last_hit[host] = time.monotonic()

    def get(self, url: str, accept: str | None = None) -> bytes | None:
        if not self.allowed(url):
            return None
        self._wait(url)
        headers = {"User-Agent": USER_AGENT}
        if accept:
            headers["Accept"] = accept
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return resp.read()
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                return None
            raise
