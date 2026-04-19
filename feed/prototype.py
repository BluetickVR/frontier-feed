"""Generate prototype plans + starter code for items marked with '!'.

When you see something at 06:45 and want to prototype it by 10:00,
tap '!' on the item. The follow-up routine generates:
1. A concrete prototype plan for YOUR stack
2. Starter code (files, commands)
3. Estimated time
4. Pushes it all to Telegram
"""
from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

from feed.llm import chat, load_context
from feed.models import Item
from feed.push import send_text
from feed.state import load_item, reactions_since

ROOT = Path(__file__).resolve().parent.parent

_SYSTEM = """You are a senior full-stack engineer helping a founder/CTO prototype AI ideas fast.

Given an AI tool/technique/repo, produce a CONCRETE prototype plan for their stack.

Their stack: React JS, Node.js, Python, AWS S3, WebSockets, Meta WhatsApp API, Ultravox, Gemini.
Their product: Real estate sales enablement (VR tours, inventory, maps, AI caller, WhatsApp bot).

Output format (strict):
## What to build
One sentence: what the prototype does, specifically for their product.

## Why this matters for PropViz
Two sentences max. Concrete business impact.

## Steps (time estimate: Xh)
1. [15min] Step description + exact command or file to create
2. [30min] Step description...
(max 6 steps, max 4 hours total)

## Starter code
```language
// The most important file — runnable, not pseudocode.
// Max 60 lines. Import real packages. Include comments for what to fill in.
```

## Test it
One command to verify it works.

Be specific. Real file paths. Real package names. Real API endpoints. No hand-waving."""


def _tavily_search(query: str) -> list[dict]:
    key = os.environ.get("TAVILY_API_KEY", "").strip()
    if not key:
        return []
    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=key)
        r = client.search(query=query, max_results=3, search_depth="advanced")
        return r.get("results", []) or []
    except Exception:
        return []


def generate_prototype(item: Item) -> str:
    ctx = load_context()
    sources = _tavily_search(f"{item.title} tutorial quickstart")
    src_block = "\n".join(
        f"[{i+1}] {s.get('title','')}: {(s.get('content') or '')[:300]}"
        for i, s in enumerate(sources[:3])
    )

    prompt = (
        f"Founder: {ctx['identity']['name']}, {ctx['identity']['role']}\n"
        f"Goal: {ctx['identity']['goal']}\n\n"
        f"Item to prototype:\n"
        f"Title: {item.title}\n"
        f"URL: {item.url}\n"
        f"Summary: {(item.summary or '')[:800]}\n\n"
        f"Reference sources:\n{src_block}\n\n"
        "Generate the prototype plan now."
    )
    return chat("synthesis", prompt, system=_SYSTEM, temperature=0.4, max_tokens=1500)


def run_prototypes(lookback_hours: int = 18) -> dict:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=lookback_hours)
    rxns = [r for r in reactions_since(cutoff) if r.char == "!"]
    prototypes = 0

    for r in rxns:
        it = load_item(r.item_id)
        if not it:
            continue
        try:
            plan = generate_prototype(it)
        except Exception as e:
            send_text(f"(prototype generation failed for <code>{it.id}</code>: {e})")
            continue

        # push to Telegram (split if too long)
        header = f"🔨 <b>Prototype plan: {it.title[:60]}</b>\n\n"
        full = header + plan
        if len(full) <= 4000:
            send_text(full, disable_preview=True)
        else:
            send_text(header + plan[:3500] + "\n\n…(cont)", disable_preview=True)
            send_text(plan[3500:], disable_preview=True)

        # save
        dir_ = ROOT / "prototypes"
        dir_.mkdir(parents=True, exist_ok=True)
        (dir_ / f"{it.id}.md").write_text(f"# Prototype: {it.title}\n\nSource: {it.url}\n\n{plan}\n")
        prototypes += 1

    return {"bang_reactions": len(rxns), "prototypes": prototypes}
