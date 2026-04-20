"""Sunday weekly synthesis — read week's journals, write trend rollup."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

from feed.llm import chat, load_context
from feed.push import send_text

ROOT = Path(__file__).resolve().parent.parent


def _week_id(now: datetime | None = None) -> str:
    now = now or datetime.now(timezone.utc)
    iso = now.isocalendar()
    return f"{iso.year}-W{iso.week:02d}"


_SYSTEM = """You are a terse, honest weekly analyst.
Given a week of journals (reactions + summaries), produce:
1. Top 3 themes I engaged with.
2. What I ignored (and whether that's a gap to fix).
3. 2 sources to consider adding.
4. 1 source to consider dropping.
5. One question for me to sit with this week.
Use headings, short sentences. Max 350 words total."""


def run_weekly_synth() -> dict:
    ROOT_JOURNALS = ROOT / "journals"
    if not ROOT_JOURNALS.exists():
        try:
            send_text("(weekly synth: no journals yet)")
        except Exception:
            pass
        return {"ok": False, "reason": "no journals directory"}

    since = datetime.now(timezone.utc) - timedelta(days=7)
    journals = []
    for p in sorted(ROOT_JOURNALS.glob("*.md")):
        try:
            stem = p.stem  # YYYY-MM-DD
            d = datetime.strptime(stem, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            if d >= since:
                journals.append(p.read_text())
        except Exception:
            continue

    if not journals:
        try:
            send_text("(weekly synth: no journals in the last 7 days)")
        except Exception:
            pass
        return {"ok": False, "reason": "no journals in the last 7 days"}

    ctx = load_context()
    prompt = (
        f"Reader: {ctx['identity']['role']}. Goal: {ctx['identity']['goal']}\n\n"
        f"Journals (last 7 days, concatenated):\n\n" + "\n\n---\n\n".join(journals)[:12000]
    )
    synth = chat("synthesis", prompt, system=_SYSTEM, temperature=0.5, max_tokens=1000)

    wk = _week_id()
    dir_ = ROOT / "strategies"
    dir_.mkdir(parents=True, exist_ok=True)
    path = dir_ / f"{wk}.md"
    path.write_text(f"# Weekly synthesis — {wk}\n\n{synth}\n")

    # push a trimmed version to Telegram
    try:
        send_text(f"<b>📈 Weekly synthesis — {wk}</b>\n\n{synth[:3200]}", disable_preview=True)
    except Exception:
        pass
    return {"ok": True, "path": str(path)}
