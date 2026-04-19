"""GitHub Trending scraper — public page, no auth needed.

Scrapes trending repos across languages we care about, filters by topic overlap
with config. Uses the HTML page because GitHub has no trending API.
"""
from __future__ import annotations

from typing import Iterable, Iterator

import httpx
from bs4 import BeautifulSoup

from feed.fetchers.base import BaseFetcher
from feed.models import Item

_URL = "https://github.com/trending/{lang}?since={since}"
_HEADERS = {
    "User-Agent": "frontier-feed/0.1 (+https://github.com/anshulpadyal/frontier-feed)",
    "Accept": "text/html",
}


class GitHubTrendingFetcher(BaseFetcher):
    name = "github_trending"

    def _pages(self) -> Iterator[tuple[str, str]]:
        since = self.cfg.get("since", "daily")
        langs = self.cfg.get("languages") or [""]
        for lang in langs:
            yield lang, _URL.format(lang=lang, since=since)

    def fetch(self) -> Iterable[Item]:
        want_topics = {t.lower() for t in self.cfg.get("topics") or []}
        max_items = int(self.cfg.get("max_items_per_run", 25))
        seen: set[str] = set()
        out: list[Item] = []

        for lang, url in self._pages():
            try:
                r = httpx.get(url, headers=_HEADERS, timeout=20, follow_redirects=True)
                r.raise_for_status()
            except Exception:
                continue

            soup = BeautifulSoup(r.text, "html.parser")
            for art in soup.select("article.Box-row"):
                a = art.select_one("h2 a")
                if not a:
                    continue
                href = a.get("href", "").strip()
                if not href.startswith("/"):
                    continue
                full_url = f"https://github.com{href}"
                if full_url in seen:
                    continue
                seen.add(full_url)

                name = " ".join(a.get_text().split())  # "owner / repo"
                desc_el = art.select_one("p")
                desc = " ".join(desc_el.get_text().split()) if desc_el else ""
                lang_el = art.select_one("[itemprop='programmingLanguage']")
                repo_lang = lang_el.get_text(strip=True) if lang_el else ""
                stars_el = art.select('a[href$="/stargazers"]')
                stars = stars_el[0].get_text(strip=True) if stars_el else ""

                # topic filter: if config lists topics, we need at least one hint in title/desc
                if want_topics:
                    hay = f"{name} {desc}".lower()
                    if not any(t in hay for t in want_topics):
                        # skim below: many ai/ml repos skip topic words in the blurb,
                        # so also include if description mentions "llm", "agent", "ai", "ml"
                        if not any(k in hay for k in ("llm", "agent", "ai", "ml",
                                                      "rag", "mcp", "claude", "gpt")):
                            continue

                meta_bits = [b for b in (repo_lang, stars and f"★ {stars}") if b]
                summary = desc
                if meta_bits:
                    summary = f"[{' · '.join(meta_bits)}] {desc}".strip()

                it = Item.new(
                    source=self.name,
                    url=full_url,
                    title=name,
                    summary=summary,
                    extra={"lang": repo_lang, "stars": stars, "trending_lang_page": lang or "all"},
                )
                out.append(it)

        # dedup by id (some repos appear on multiple language pages)
        by_id: dict[str, Item] = {}
        for it in out:
            by_id.setdefault(it.id, it)
        # cap
        return list(by_id.values())[:max_items]
