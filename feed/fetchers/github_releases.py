"""GitHub Releases fetcher — watches specific repos from context.yaml watchlist."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

import httpx
import yaml

from feed.fetchers.base import BaseFetcher
from feed.models import Item

_API_URL = "https://api.github.com/repos/{owner}/{repo}/releases?per_page=5"
_HEADERS = {
    "User-Agent": "frontier-feed/0.1 (+https://github.com/anshulpadyal/frontier-feed)",
    "Accept": "application/vnd.github+json",
}

# Match owner/repo from URLs like https://github.com/anthropics/claude-code/releases.atom
_REPO_RE = re.compile(r"github\.com/([^/]+)/([^/]+)")


def _repos_from_context() -> list[tuple[str, str]]:
    """Extract (owner, repo) pairs from context.yaml watchlist.tool_changelogs."""
    ctx_path = Path(__file__).resolve().parents[2] / "context.yaml"
    if not ctx_path.exists():
        return []
    try:
        ctx = yaml.safe_load(ctx_path.read_text())
    except Exception:
        return []
    urls = (ctx.get("watchlist") or {}).get("tool_changelogs") or []
    repos: list[tuple[str, str]] = []
    for url in urls:
        m = _REPO_RE.search(url)
        if m:
            repos.append((m.group(1), m.group(2)))
    return repos


class GitHubReleasesFetcher(BaseFetcher):
    name = "github_releases"

    def fetch(self) -> Iterable[Item]:
        repos = _repos_from_context()
        if not repos:
            return []

        out: list[Item] = []

        for owner, repo in repos:
            url = _API_URL.format(owner=owner, repo=repo)
            try:
                r = httpx.get(url, headers=_HEADERS, timeout=20)
                r.raise_for_status()
                releases = r.json()
            except Exception:
                continue

            if not isinstance(releases, list):
                continue

            for rel in releases:
                tag = rel.get("tag_name", "")
                name = rel.get("name", "") or tag
                body = rel.get("body", "") or ""
                html_url = rel.get("html_url", "")
                published = rel.get("published_at", "")

                if not html_url:
                    continue

                title = f"{owner}/{repo} {name}"
                # Truncate body for summary
                body_short = body[:300].replace("\n", " ").strip()
                if len(body) > 300:
                    body_short += "..."

                summary = f"[{tag}] {body_short}" if body_short else f"[{tag}]"

                it = Item.new(
                    source=self.name,
                    url=html_url,
                    title=title,
                    summary=summary,
                    extra={
                        "tag_name": tag,
                        "release_name": name,
                        "published_at": published,
                        "owner": owner,
                        "repo": repo,
                    },
                )
                out.append(it)

        return out
