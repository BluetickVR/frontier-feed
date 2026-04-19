"""Show HN + top AI stories via HN Algolia API."""
from __future__ import annotations

from typing import Iterable

import httpx

from feed.fetchers.base import BaseFetcher
from feed.models import Item

_SHOW_HN_URL = "https://hn.algolia.com/api/v1/search?tags=show_hn&query={query}"
_STORIES_URL = "https://hn.algolia.com/api/v1/search?tags=story&query={query}"
_HN_ITEM = "https://news.ycombinator.com/item?id={id}"
_HEADERS = {
    "User-Agent": "frontier-feed/0.1 (+https://github.com/anshulpadyal/frontier-feed)",
    "Accept": "application/json",
}


class ShowHNFetcher(BaseFetcher):
    name = "show_hn"

    def fetch(self) -> Iterable[Item]:
        max_items = int(self.cfg.get("max_items_per_run", 15))
        tags = self.cfg.get("tags") or ["ai", "llm", "agent", "ml"]
        query = "+".join(tags)

        seen: set[str] = set()
        out: list[Item] = []

        for url_tpl in (_SHOW_HN_URL, _STORIES_URL):
            url = url_tpl.format(query=query)
            try:
                r = httpx.get(url, headers=_HEADERS, timeout=20)
                r.raise_for_status()
                data = r.json()
            except Exception:
                continue

            for hit in data.get("hits", []):
                object_id = hit.get("objectID", "")
                title = hit.get("title") or ""
                if not title:
                    continue

                story_url = hit.get("url") or _HN_ITEM.format(id=object_id)
                if story_url in seen:
                    continue
                seen.add(story_url)

                points = hit.get("points", 0)
                num_comments = hit.get("num_comments", 0)
                author = hit.get("author", "")

                hn_link = _HN_ITEM.format(id=object_id)
                meta = f"[{points} pts · {num_comments} comments]"
                summary = f"{meta} {title}"

                it = Item.new(
                    source=self.name,
                    url=story_url,
                    title=title,
                    summary=summary,
                    extra={
                        "points": points,
                        "num_comments": num_comments,
                        "author": author,
                        "hn_url": hn_link,
                    },
                )
                out.append(it)

        # Sort by points descending, then cap
        out.sort(key=lambda x: x.extra.get("points", 0), reverse=True)
        return out[:max_items]
