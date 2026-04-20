"""Two-pass relevance scoring.

Pass 1 (Groq, cheap): quick topic relevance filter — kills obvious noise.
Pass 2 (Groq 70B, smarter): "Would the founder of the world's #1 real estate
tech company stop scrolling for this?" — reranks survivors.
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Iterable

from feed.llm import chat, load_context

ROOT = Path(__file__).resolve().parent.parent
from feed.models import Item
from feed.state import weight_for


_PASS1_SYSTEM = """Score 0-1. Return ONLY: {"score": 0.X, "why": "short reason"}
HIGH 0.8+: voice AI, 3D rendering, spatial computing, WebGL/Three.js, generative 3D, AR/VR
MEDIUM 0.5-0.7: agent frameworks, AI coding tools, foundation models, MCP
LOW 0.2-0.4: generic AI repos, RAG frameworks, tutorials
ZERO 0.0-0.1: crypto, ethics papers, unrelated tools
No markdown. No explanation. Just the JSON object."""


_PASS2_SYSTEM = """Re-score for a CTO building #1 real estate tech company (VR tours, 3D maps, AI voice caller, WhatsApp bot).
Stack: React, Node, Python, Ultravox, Three.js, WebSockets, AWS.
Question: "Will this help build something no other real estate tech company has?"
0.9: 3D/voice/spatial breakthrough directly applicable to property sales
0.7: dev velocity tool that makes 8 devs ship like 40
0.5: useful AI tool, no specific real estate angle
0.3: generic trending repo
Return ONLY: {"score": 0.X, "why": "how it applies to 3D/voice/sales"}
No markdown. Just JSON."""


_JSON_RE = re.compile(r"\{.*\}", re.DOTALL)


@lru_cache
def _load_stack_summary() -> str:
    """Load condensed stack graph summaries from stack/ folder."""
    stack_dir = ROOT / "stack"
    if not stack_dir.exists():
        return ""
    parts = []
    for f in sorted(stack_dir.glob("*-summary.md")):
        text = f.read_text()
        # Just take Architecture + Technologies sections (compact)
        for line in text.split("\n"):
            if line.startswith("- **") or line.startswith("- Runtime") or line.startswith("- Database") or line.startswith("- Storage") or line.startswith("- Real-time") or line.startswith("- Media") or line.startswith("- Display") or line.startswith("- Auth"):
                parts.append(line.strip("- ").strip())
    return "; ".join(parts[:20]) if parts else ""


def _context_blurb() -> str:
    stack = _load_stack_summary()
    base = "CTO building #1 real estate tech company. Products: VR tours, 3D maps, AI voice caller, WhatsApp bot, TV CMS."
    if stack:
        base += f" Actual stack (from code graph): {stack[:400]}"
    return base


def _parse(raw: str) -> tuple[float, str]:
    cleaned = raw.replace("```json", "").replace("```", "").strip()
    m = _JSON_RE.search(cleaned)
    if not m:
        return 0.0, ""
    try:
        d = json.loads(m.group(0))
        return float(d.get("score", 0.0)), str(d.get("why", "")).strip()
    except Exception:
        return 0.0, ""


def _chat_with_fallback(task: str, prompt: str, system: str,
                        temperature: float = 0.1, max_tokens: int = 120) -> str:
    """Try primary provider, fall back to gemini on rate limit."""
    try:
        return chat(task, prompt, system=system, temperature=temperature, max_tokens=max_tokens)
    except Exception as e:
        if "rate_limit" in str(e).lower() or "429" in str(e):
            try:
                return chat("synthesis", prompt, system=system,
                          temperature=temperature, max_tokens=max_tokens)
            except Exception:
                pass
        raise


def _score_pass1(it: Item) -> Item:
    body = (it.summary or "")[:600]
    extra_context = ""
    if it.source == "watchlist_twitter":
        eng = it.extra.get("engagement", 0)
        handle = it.extra.get("handle", "")
        extra_context = f"\nPosted by: @{handle} (engagement: {eng} likes+RTs). This is from a top AI researcher/builder's Twitter."
    elif it.source == "hf_papers":
        comments = it.extra.get("comments", 0)
        extra_context = f"\nHuggingFace trending paper ({comments} comments). Research frontier."
    prompt = (
        f"{_context_blurb()}\n\n"
        f"Item: [{it.source}] {it.title}\n"
        f"URL: {it.url}\n"
        f"Summary: {body}{extra_context}\n"
    )
    raw = _chat_with_fallback("classify", prompt, system=_PASS1_SYSTEM,
                              temperature=0.1, max_tokens=256)
    score, why = _parse(raw)
    it.raw_score = score
    it.why_it_matters = why
    it.score = round(score * weight_for(it.source), 3)
    return it


def _score_pass2(it: Item) -> Item:
    body = (it.summary or "")[:800]
    prompt = (
        f"Item: [{it.source}] {it.title}\n"
        f"URL: {it.url}\n"
        f"Summary: {body}\n"
        f"Pass 1 score: {it.raw_score} — {it.why_it_matters}\n"
    )
    raw = _chat_with_fallback("rank", prompt, system=_PASS2_SYSTEM,
                              temperature=0.2, max_tokens=256)
    score, why = _parse(raw)
    if why:
        it.why_it_matters = why
    blended = (score * 0.7) + (it.raw_score * 0.3)
    it.score = round(blended * weight_for(it.source), 3)
    return it


def score_all(items: Iterable[Item], pass2_top_n: int = 30) -> list[Item]:
    """Two-pass scoring: cheap filter on all, smart rerank on top N."""
    # Pass 1: quick score everything (8B model, cheap)
    scored: list[Item] = []
    for it in items:
        try:
            scored.append(_score_pass1(it))
        except Exception as e:
            # Default to 0.4 so rate-limited items still appear in tier 2
            it.raw_score = 0.4
            it.score = round(0.4 * weight_for(it.source), 3)
            it.why_it_matters = "(scoring unavailable — defaulted)"
            scored.append(it)

    # Sort by pass1 score
    scored.sort(key=lambda x: x.score, reverse=True)

    # Pass 2: rerank top N with the harder question
    for it in scored[:pass2_top_n]:
        try:
            _score_pass2(it)
        except Exception:
            pass  # keep pass1 score

    # Re-sort by final score
    scored.sort(key=lambda x: x.score, reverse=True)
    return scored
