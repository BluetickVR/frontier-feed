"""HuggingFace Daily Papers — uses the API for trending research."""
from __future__ import annotations

from typing import Iterable

import httpx

from feed.fetchers.base import BaseFetcher
from feed.models import Item

_API_URL = "https://huggingface.co/api/daily_papers"


class HFPapersFetcher(BaseFetcher):
    name = "hf_papers"

    def fetch(self) -> Iterable[Item]:
        max_items = int(self.cfg.get("max_items_per_run", 10))

        try:
            r = httpx.get(_API_URL, timeout=20)
            r.raise_for_status()
            papers = r.json()
        except Exception:
            return []

        if not isinstance(papers, list):
            return []

        out: list[Item] = []
        for p in papers[:max_items]:
            paper_id = p.get("paper", {}).get("id", "")
            title = p.get("title", "")
            summary_text = p.get("summary", "")[:500]
            comments = p.get("numComments", 0)
            submitter = p.get("submittedBy", {})
            submitter_name = submitter.get("fullname", "") if isinstance(submitter, dict) else ""

            url = f"https://huggingface.co/papers/{paper_id}" if paper_id else ""
            if not url or not title:
                continue

            summary = f"[{comments} comments] {summary_text}" if comments else summary_text

            it = Item.new(
                source=self.name,
                url=url,
                title=title,
                summary=summary,
                extra={"paper_id": paper_id, "comments": comments, "submitter": submitter_name},
            )
            out.append(it)

        return out
