"""Handle '!' reactions — trigger a Claude Code routine to write a prototype PR.

Flow:
1. User taps ! on a digest item
2. At 13:00, this module reads ! reactions
3. For each one: Tavily-searches the item, generates a detailed brief,
   and triggers a Claude Code routine on propviz-prototypes repo
4. That routine writes the code, creates a branch, opens a PR
5. Sends the PR link to Telegram
"""
from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

import httpx

from feed.llm import chat, load_context
from feed.models import Item
from feed.push import send_text
from feed.state import load_item, reactions_since

ROOT = Path(__file__).resolve().parent.parent

_BRIEF_SYSTEM = """You write prototype briefs for a CTO's AI assistant to implement.
The assistant will receive this brief and write actual running code.

Output a JSON object with these fields:
  "title": short name for the prototype (slug-friendly, e.g. "mcp-inventory-agent")
  "description": 2-sentence description of what to build
  "stack": which tech to use (from: React, Node.js, Python, FastAPI, Ultravox, Meta WhatsApp API, WebSockets, AWS S3)
  "files": list of files to create with descriptions, e.g. [{"path": "src/agent.py", "desc": "Main agent with 3 tools"}]
  "test_command": one command to verify it works
  "business_context": why this matters for PropViz (real estate sales enablement, AI caller, WhatsApp bot, VR tours)

Output ONLY valid JSON."""


def _tavily_search(query: str) -> list[dict]:
    key = os.environ.get("TAVILY_API_KEY", "").strip()
    if not key:
        return []
    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=key)
        r = client.search(query=query, max_results=5, search_depth="advanced")
        return r.get("results", []) or []
    except Exception:
        return []


def _generate_brief(item: Item, sources: list[dict]) -> dict:
    ctx = load_context()
    src_block = "\n".join(
        f"[{i+1}] {s.get('title','')}\n{(s.get('content') or '')[:400]}"
        for i, s in enumerate(sources[:5])
    )
    prompt = (
        f"CTO: {ctx['identity']['name']}, {ctx['identity']['role']}\n"
        f"Product: Real estate sales enablement — VR tours, inventory, maps, AI caller (Ultravox), "
        f"WhatsApp bot (Meta API), session recording, EOI platform\n"
        f"Stack: React JS, Node.js, Python, AWS S3, WebSockets, Meta WhatsApp API, Ultravox, Gemini\n\n"
        f"Item to prototype:\n"
        f"Title: {item.title}\n"
        f"URL: {item.url}\n"
        f"Summary: {(item.summary or '')[:800]}\n\n"
        f"Sources:\n{src_block}\n\n"
        f"Generate the prototype brief JSON."
    )
    raw = chat("synthesis", prompt, system=_BRIEF_SYSTEM, temperature=0.3, max_tokens=800)
    import re
    m = re.search(r"\{.*\}", raw, re.DOTALL)
    if m:
        return json.loads(m.group(0))
    return {"title": "prototype", "description": item.title, "stack": "Python",
            "files": [], "test_command": "echo ok", "business_context": ""}


def _trigger_prototype_routine(brief: dict, item: Item) -> str | None:
    """Fire a one-shot Claude Code routine on propviz-prototypes to write the code."""
    slug = brief.get("title", "prototype").replace(" ", "-").lower()[:40]
    branch = f"proto/{slug}-{datetime.now(timezone.utc).strftime('%m%d')}"

    prompt = (
        f"You are building a prototype in the propviz-prototypes repo.\n\n"
        f"## What to build\n"
        f"{brief.get('description', '')}\n\n"
        f"## Business context\n"
        f"{brief.get('business_context', '')}\n\n"
        f"## Stack\n"
        f"{brief.get('stack', 'Python')}\n\n"
        f"## Files to create\n"
        f"{json.dumps(brief.get('files', []), indent=2)}\n\n"
        f"## Source reference\n"
        f"URL: {item.url}\n"
        f"Summary: {(item.summary or '')[:500]}\n\n"
        f"## Instructions\n"
        f"1. Create branch `{branch}` from main\n"
        f"2. Create a folder `{slug}/` with all the files\n"
        f"3. Include a `{slug}/README.md` explaining what this is, how to run it, and why it matters\n"
        f"4. Include a `{slug}/requirements.txt` or `{slug}/package.json` as appropriate\n"
        f"5. Write REAL, RUNNING code. Not pseudocode. Use real package names and APIs.\n"
        f"6. Test command should work: `{brief.get('test_command', 'echo ok')}`\n"
        f"7. Commit all files\n"
        f"8. Push the branch\n"
        f"9. Open a PR to main with title: `proto: {brief.get('description', slug)[:60]}`\n"
        f"   PR body should explain what this prototype does and how to test it.\n"
        f"10. Report the PR URL.\n"
    )

    trigger_body = {
        "name": f"prototype-{slug}",
        "cron_expression": "0 0 1 1 *",  # dummy cron, we'll run it manually
        "enabled": False,  # don't auto-run
        "job_config": {
            "ccr": {
                "environment_id": "env_01NgQFQ9xYHER3kqiQgCChiJ",
                "session_context": {
                    "model": "claude-sonnet-4-6",
                    "sources": [{"git_repository": {"url": "https://github.com/BluetickVR/propviz-prototypes"}}],
                    "allowed_tools": ["Bash", "Read", "Write", "Edit", "Glob", "Grep"],
                },
                "events": [{
                    "data": {
                        "uuid": str(uuid.uuid4()),
                        "session_id": "",
                        "type": "user",
                        "parent_tool_use_id": None,
                        "message": {"content": prompt, "role": "user"},
                    }
                }],
            }
        },
    }

    # Use the RemoteTrigger API via direct HTTP
    # The Claude Code CLI auth token is in the keychain — we use httpx with the session
    try:
        # Create the trigger
        from feed.trigger_api import create_and_run_trigger
        return create_and_run_trigger(trigger_body)
    except Exception as e:
        print(f"[prototype] trigger failed: {e}")
        return None


def run_prototypes(lookback_hours: int = 18) -> dict:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=lookback_hours)
    rxns = [r for r in reactions_since(cutoff) if r.char == "!"]
    triggered = 0

    for r in rxns:
        it = load_item(r.item_id)
        if not it:
            continue

        send_text(f"🔨 Generating prototype for: <b>{it.title[:60]}</b>...", disable_preview=True)

        # Research the item
        query = f"{it.title} quickstart tutorial example code"[:200]
        sources = _tavily_search(query)

        # Generate the brief
        try:
            brief = _generate_brief(it, sources)
        except Exception as e:
            send_text(f"(brief generation failed for {it.id}: {e})")
            continue

        # Save the brief
        dir_ = ROOT / "prototypes"
        dir_.mkdir(parents=True, exist_ok=True)
        (dir_ / f"{it.id}.json").write_text(json.dumps(brief, indent=2))

        # Try to trigger a Claude Code routine
        result = _trigger_prototype_routine(brief, it)
        if result:
            send_text(
                f"🚀 Prototype routine triggered for <b>{brief.get('title','')}</b>\n"
                f"Check: https://claude.ai/code/scheduled\n"
                f"PR will appear in BluetickVR/propviz-prototypes",
                disable_preview=True,
            )
            triggered += 1
        else:
            # Fallback: just send the brief to Telegram
            files_str = "\n".join(f"  - {f['path']}: {f.get('desc','')}" for f in brief.get("files", []))
            send_text(
                f"🔨 <b>Prototype brief: {brief.get('title','')}</b>\n\n"
                f"{brief.get('description','')}\n\n"
                f"<b>Stack:</b> {brief.get('stack','')}\n"
                f"<b>Files:</b>\n{files_str}\n"
                f"<b>Test:</b> <code>{brief.get('test_command','')}</code>\n\n"
                f"<i>{brief.get('business_context','')}</i>",
                disable_preview=True,
            )

    return {"bang_reactions": len(rxns), "triggered": triggered}
