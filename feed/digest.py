"""Orchestrator: fetch → rank → select → write markdown → push."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Optional

from feed.fetchers import build_fetcher
from feed.llm import load_config, load_context
from feed.models import Item
from feed.push import push_items, send_text
from feed.score import score_all
from feed.state import (
    get_pointer,
    log_items,
    reacted_item_ids,
    save_pointer,
    seen_item_ids,
)

ROOT = Path(__file__).resolve().parent.parent


def _cfg():
    return load_config()


def _threshold() -> float:
    return float(load_context()["budgets"]["relevance_threshold"])


def _budget(slot: str) -> int:
    b = load_context()["budgets"]
    return int(b["morning_push_max_items"] if slot == "morning" else b["evening_push_max_items"])


def _enabled_fetchers(only: Optional[list[str]] = None) -> list[tuple[str, dict]]:
    cfg = _cfg()
    out: list[tuple[str, dict]] = []
    for name, fcfg in cfg["fetchers"].items():
        if not fcfg.get("enabled"):
            continue
        if only and name not in only:
            continue
        out.append((name, fcfg))
    return out


def _fetch(only: Optional[list[str]] = None) -> list[Item]:
    items: list[Item] = []
    for name, fcfg in _enabled_fetchers(only):
        try:
            f = build_fetcher(name, fcfg)
            for it in f.fetch():
                items.append(it)
        except Exception as e:
            # surface but don't crash
            print(f"[fetch] {name} failed: {e}")
    return items


def _filter_unseen(items: list[Item]) -> list[Item]:
    seen = seen_item_ids()
    reacted = reacted_item_ids()
    return [i for i in items if i.id not in seen and i.id not in reacted]


def _select(items: list[Item], n: int) -> list[Item]:
    th = _threshold()
    passing = [i for i in items if i.score >= th]
    return passing[:n]


def _digest_md(slot: str, selected: list[Item], all_ranked: list[Item]) -> str:
    now = datetime.now(timezone.utc)
    ymd = now.strftime("%Y-%m-%d")
    lines = [
        f"# Digest {ymd} — {slot}",
        "",
        f"_threshold={_threshold()}  fetched={len(all_ranked)}  selected={len(selected)}_",
        "",
        "## Selected",
    ]
    for it in selected:
        lines.append(f"- **[{it.source}]** [{it.title}]({it.url}) — score {it.score}")
        if it.why_it_matters:
            lines.append(f"  _{it.why_it_matters}_")
    lines.append("")
    lines.append("## Ranked (not selected)")
    for it in all_ranked:
        if it in selected:
            continue
        lines.append(f"- [{it.source}] [{it.title}]({it.url}) — score {it.score}")
    lines.append("")
    return "\n".join(lines)


def _write_digest(slot: str, content: str) -> Path:
    now = datetime.now(timezone.utc)
    dir_ = ROOT / _cfg()["paths"]["digests_dir"]
    dir_.mkdir(parents=True, exist_ok=True)
    path = dir_ / f"{now.strftime('%Y-%m-%d')}-{slot}.md"
    path.write_text(content)
    return path


def run_digest(slot: str = "morning", only: Optional[list[str]] = None,
               push: bool = True, dry_run: bool = False) -> dict:
    """Full digest cycle. slot ∈ {morning, evening}."""
    raw = _fetch(only)
    fresh = _filter_unseen(raw)
    ranked = score_all(fresh)
    n = _budget(slot)
    selected = _select(ranked, n)

    # log items so we never re-rank them
    log_items(ranked)

    md = _digest_md(slot, selected, ranked)
    path = _write_digest(slot, md)

    if dry_run:
        return {"path": str(path), "fetched": len(raw), "fresh": len(fresh),
                "ranked": len(ranked), "selected": len(selected), "pushed": 0}

    pushed: list[Item] = []
    if push:
        if not selected:
            send_text(f"🤫 quiet {slot} — nothing above threshold (fetched {len(raw)})")
        else:
            header = f"🔔 {slot.title()} — {len(selected)} items"
            pushed = push_items(selected, header=header)
            # re-log with pushed metadata
            log_items(pushed)

    # advance pointers
    now = datetime.now(timezone.utc)
    for name, _ in _enabled_fetchers(only):
        save_pointer(name, now)

    return {"path": str(path), "fetched": len(raw), "fresh": len(fresh),
            "ranked": len(ranked), "selected": len(selected), "pushed": len(pushed)}
