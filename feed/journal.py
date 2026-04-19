"""Nightly: read today's reactions → retune weights → write journal."""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

from feed.llm import chat
from feed.push import send_text
from feed.state import load_item, reactions_since, retune_weights

ROOT = Path(__file__).resolve().parent.parent


def run_journal() -> dict:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    rxns = reactions_since(cutoff)
    by_char = Counter(r.char for r in rxns)
    weights = retune_weights()

    lines: list[str] = []
    for r in rxns:
        it = load_item(r.item_id)
        if not it:
            continue
        lines.append(f"- `{r.char}` [{it.source}] {it.title}  — {it.url}")

    ymd = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    md = [
        f"# Journal {ymd}",
        "",
        f"Reactions: total={len(rxns)}  read={by_char.get('.',0)}  "
        f"q={by_char.get('?',0)}  +={by_char.get('+',0)}  -={by_char.get('-',0)}",
        "",
        "## Reactions by item",
        *lines,
        "",
        "## Weights after retune",
        *(f"- `{k}`: {v}" for k, v in sorted(weights.items())),
        "",
    ]
    if rxns:
        # short narrative summary
        try:
            raw = chat(
                "summarize",
                f"Summarize this reaction set in 2 sentences, noting themes: {by_char}\n"
                f"Items reacted to:\n" + "\n".join(lines[:25]),
                system="You are terse. Exactly 2 sentences.",
                temperature=0.3,
                max_tokens=160,
            )
            md += ["## Summary", raw, ""]
        except Exception:
            pass

    dir_ = ROOT / "journals"
    dir_.mkdir(parents=True, exist_ok=True)
    path = dir_ / f"{ymd}.md"
    path.write_text("\n".join(md))

    try:
        send_text(
            f"🌙 journal saved — {len(rxns)} reactions · "
            f"{by_char.get('.',0)} read / {by_char.get('?',0)}? / "
            f"{by_char.get('+',0)}+ / {by_char.get('-',0)}−",
            disable_preview=True,
        )
    except Exception:
        pass

    return {"reactions": len(rxns), "weights": weights, "path": str(path)}
