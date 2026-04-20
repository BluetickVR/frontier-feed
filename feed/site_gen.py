"""Generate static site from digest items + audio briefings."""
from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone, timedelta
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from feed.models import Item
from feed.state import ITEMS_FILE

ROOT = Path(__file__).resolve().parent.parent
SITE_DIR = ROOT / "site"
DIST_DIR = SITE_DIR / "dist"
TEMPLATE_DIR = SITE_DIR / "templates"
AUDIO_DIR = SITE_DIR / "audio"


def _load_all_items() -> list[Item]:
    items: list[Item] = []
    if not ITEMS_FILE.exists():
        return items
    with ITEMS_FILE.open() as f:
        for line in f:
            if not line.strip():
                continue
            try:
                items.append(Item.model_validate_json(line))
            except Exception:
                continue
    return items


def _group_by_date(items: list[Item]) -> dict[str, list[Item]]:
    groups: dict[str, list[Item]] = {}
    for it in items:
        d = (it.pushed_at or it.first_seen).strftime("%Y-%m-%d")
        groups.setdefault(d, []).append(it)
    for k in groups:
        groups[k].sort(key=lambda x: x.score, reverse=True)
    return groups


def generate_site() -> dict:
    """Generate static HTML site in site/dist/."""
    DIST_DIR.mkdir(parents=True, exist_ok=True)

    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))
    template = env.get_template("index.html")

    items = _load_all_items()
    by_date = _group_by_date(items)

    # Sort dates newest first
    sorted_dates = sorted(by_date.keys(), reverse=True)
    if not sorted_dates:
        sorted_dates = [datetime.now(timezone.utc).strftime("%Y-%m-%d")]

    pages_generated = 0

    for i, date_str in enumerate(sorted_dates[:14]):  # last 14 days
        day_items = by_date.get(date_str, [])
        all_items = [it for it in day_items if it.score > 0]

        # Check for audio
        audio_file = None
        for slot in ("morning", "evening"):
            audio_name = f"{date_str}-{slot}.mp3"
            audio_src = AUDIO_DIR / audio_name
            if audio_src.exists():
                audio_dst = DIST_DIR / "audio" / audio_name
                audio_dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(audio_src, audio_dst)
                audio_file = f"audio/{audio_name}"
                break

        # Date navigation
        dates = []
        for j, d in enumerate(sorted_dates[:14]):
            dt = datetime.strptime(d, "%Y-%m-%d")
            dates.append({
                "file": f"{d}.html" if j != 0 else "index.html",
                "label": dt.strftime("%b %d"),
                "active": d == date_str,
            })

        html = template.render(
            all_items=all_items,
            dates=dates,
            date_label=datetime.strptime(date_str, "%Y-%m-%d").strftime("%A, %B %d"),
            slot="morning",
            audio_file=audio_file,
        )

        filename = "index.html" if i == 0 else f"{date_str}.html"
        (DIST_DIR / filename).write_text(html)
        pages_generated += 1

    return {"pages": pages_generated, "dist": str(DIST_DIR)}
