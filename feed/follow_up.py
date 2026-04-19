"""Handle '?' reactions → deep-search + synthesize dossier → push."""
from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from feed.llm import chat, load_context
from feed.models import Item
from feed.push import push_dossier, send_text
from feed.state import load_item, reactions_since

ROOT = Path(__file__).resolve().parent.parent


def _tavily_search(query: str, max_results: int = 5) -> list[dict]:
    key = os.environ.get("TAVILY_API_KEY", "").strip()
    if not key:
        return []
    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=key)
        r = client.search(query=query, max_results=max_results, include_answer=True,
                          search_depth="advanced")
        return r.get("results", []) or []
    except Exception as e:
        print(f"[tavily] failed: {e}")
        return []


_SYSTEM = """You write 2-paragraph briefings for a founder/CTO.
Paragraph 1: what the thing is, in concrete terms, using primary-source evidence.
Paragraph 2: why it matters to them given their context (role, goals, business).
Cite primary sources inline as [1], [2], etc. matching the numbered list you were given.
No filler, no 'in conclusion', no bullet lists. Two tight paragraphs. Max 220 words."""


def _briefing(item: Item, sources: list[dict]) -> str:
    ctx = load_context()
    src_block = "\n".join(
        f"[{i+1}] {s.get('title','')}\n{s.get('url','')}\n{(s.get('content') or '')[:500]}"
        for i, s in enumerate(sources[:5])
    )
    prompt = (
        f"Reader context: {ctx['identity']['role']}. Goal: {ctx['identity']['goal']}\n\n"
        f"Item: {item.title}\nURL: {item.url}\nSummary: {item.summary or ''}\n\n"
        f"Sources:\n{src_block}\n\n"
        "Write the 2-paragraph briefing now."
    )
    return chat("synthesis", prompt, system=_SYSTEM, temperature=0.4, max_tokens=600)


def run_follow_ups(lookback_hours: int = 18) -> dict:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=lookback_hours)
    rxns = [r for r in reactions_since(cutoff) if r.char == "?"]
    dossiers = 0
    for r in rxns:
        it = load_item(r.item_id)
        if not it:
            continue
        query = f"{it.title} — {it.summary or ''}"[:300]
        sources = _tavily_search(query)
        if not sources:
            send_text(f"(no follow-up sources found for <code>{it.id}</code>)")
            continue
        try:
            briefing = _briefing(it, sources)
        except Exception as e:
            send_text(f"(dossier synthesis failed for <code>{it.id}</code>: {e})")
            continue
        push_dossier(it, briefing)
        # save dossier file
        dir_ = ROOT / "dossiers"
        dir_.mkdir(parents=True, exist_ok=True)
        (dir_ / f"{it.id}.md").write_text(
            f"# {it.title}\n\nSource: {it.url}\n\n{briefing}\n"
        )
        dossiers += 1
    if dossiers == 0 and rxns:
        send_text("(follow-ups ran but produced no dossiers)")
    return {"questions": len(rxns), "dossiers": dossiers}
