"""Relevance scoring — LLM + source weight."""
from __future__ import annotations

import json
import re
from typing import Iterable

from feed.llm import chat, load_context
from feed.models import Item
from feed.state import weight_for


_SYSTEM = """You score AI-frontier items for a founder/CTO building agent infra.
Return a JSON object with two fields:
  "score": float in [0,1] — relevance to their interests
  "why":   short string (<= 18 words) — why it matters to THEM specifically.
Be strict. Generic AI articles score low. Applied, tool/repo/model-specific items score high.
Output ONLY valid JSON, nothing else."""


def _context_blurb() -> str:
    ctx = load_context()
    parts = [
        f"Identity: {ctx['identity']['role']}",
        f"Goal: {ctx['identity']['goal']}",
        "Top priority topics: " + "; ".join(ctx["topics"]["top_priority"]),
        "High: " + "; ".join(ctx["topics"]["high"]),
        "Deprioritize: " + "; ".join(ctx["topics"]["deprioritize"]),
    ]
    return "\n".join(parts)


_JSON_RE = re.compile(r"\{.*\}", re.DOTALL)


def _parse(raw: str) -> tuple[float, str]:
    m = _JSON_RE.search(raw)
    if not m:
        return 0.0, ""
    try:
        d = json.loads(m.group(0))
        return float(d.get("score", 0.0)), str(d.get("why", "")).strip()
    except Exception:
        return 0.0, ""


def score_item(it: Item) -> Item:
    body = (it.summary or "")[:800]
    prompt = (
        f"{_context_blurb()}\n\n"
        f"Item:\n"
        f"  source: {it.source}\n"
        f"  title: {it.title}\n"
        f"  url: {it.url}\n"
        f"  summary: {body}\n"
    )
    raw = chat("rank", prompt, system=_SYSTEM, temperature=0.1, max_tokens=150)
    raw_score, why = _parse(raw)
    it.raw_score = raw_score
    it.why_it_matters = why or it.why_it_matters
    it.score = round(raw_score * weight_for(it.source), 3)
    return it


def score_all(items: Iterable[Item]) -> list[Item]:
    out: list[Item] = []
    for it in items:
        try:
            out.append(score_item(it))
        except Exception as e:
            # don't let one bad item kill the batch
            it.raw_score = 0.0
            it.score = 0.0
            it.why_it_matters = f"(scoring failed: {e})"
            out.append(it)
    return sorted(out, key=lambda x: x.score, reverse=True)
