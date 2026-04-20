"""Two-pass relevance scoring.

Pass 1 (Groq, cheap): quick topic relevance filter — kills obvious noise.
Pass 2 (Groq 70B, smarter): "Would the founder of the world's #1 real estate
tech company stop scrolling for this?" — reranks survivors.
"""
from __future__ import annotations

import json
import re
from typing import Iterable

from feed.llm import chat, load_context
from feed.models import Item
from feed.state import weight_for


_PASS1_SYSTEM = """You score items for relevance to a real estate tech founder building the #1 company in the world using AI + 3D tech.
Return JSON: {"score": float 0-1, "why": "<12 words max>"}
Score HIGH (0.7+): voice AI, 3D/spatial, agent frameworks, AI coding tools, generative 3D, PropTech AI, real-time rendering, browser automation
Score MEDIUM (0.4-0.7): foundation model releases, AI infra, enterprise AI, MCP, embeddings
Score LOW (<0.4): generic AI content, crypto, ethics debates, social media tools
Output ONLY valid JSON."""


_PASS2_SYSTEM = """You are re-ranking AI items for Anshul Padyal.

He is building the #1 real estate tech company in the world. His company (PropViz, acquired by MagicBricks/Times Group) has 80+ builder clients, VR tours, 3D maps, AI voice caller, WhatsApp AI bot, and MagicBricks distribution.

His edge: AI + 3D tech applied to property sales at a scale nobody else attempts.
His stack: React, Node, Python, Ultravox, Meta WhatsApp API, WebSockets, AWS, Three.js.
His team: 8 devs + 2 PMs. Every tool that makes them 10x faster matters.

For each item, answer:
1. Could this become a feature/capability no other real estate tech company has?
2. Could this make his team ship 2-5x faster?
3. Is this something he should know about before his competitors do?

Return JSON: {"score": float 0-1, "why": "<18 words — be specific about HOW it applies to his business>"}
Be brutal. Generic "useful for AI" = 0.3. "This lets his AI caller handle 10 languages with zero latency" = 0.95.
Output ONLY valid JSON."""


_JSON_RE = re.compile(r"\{.*\}", re.DOTALL)


def _context_blurb() -> str:
    ctx = load_context()
    identity = ctx["identity"]
    parts = [
        f"Identity: {identity['name']}, {identity['role']}",
        f"Ambition: {identity['ambition']}",
        f"What they have: {identity['what_we_have']}",
        f"What they need: {identity['what_we_need']}",
        f"Scoring lens: {identity['scoring_lens']}",
        "Top priority topics: " + "; ".join(ctx["topics"]["top_priority"]),
        "High: " + "; ".join(ctx["topics"]["high"]),
        "Deprioritize: " + "; ".join(ctx["topics"]["deprioritize"]),
    ]
    return "\n".join(parts)


def _parse(raw: str) -> tuple[float, str]:
    m = _JSON_RE.search(raw)
    if not m:
        return 0.0, ""
    try:
        d = json.loads(m.group(0))
        return float(d.get("score", 0.0)), str(d.get("why", "")).strip()
    except Exception:
        return 0.0, ""


def _score_pass1(it: Item) -> Item:
    body = (it.summary or "")[:600]
    prompt = (
        f"{_context_blurb()}\n\n"
        f"Item: [{it.source}] {it.title}\n"
        f"URL: {it.url}\n"
        f"Summary: {body}\n"
    )
    raw = chat("rank", prompt, system=_PASS1_SYSTEM, temperature=0.1, max_tokens=120)
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
    raw = chat("rank", prompt, system=_PASS2_SYSTEM, temperature=0.2, max_tokens=150)
    score, why = _parse(raw)
    if why:
        it.why_it_matters = why
    # pass2 score blends with pass1 (70% pass2, 30% pass1)
    blended = (score * 0.7) + (it.raw_score * 0.3)
    it.score = round(blended * weight_for(it.source), 3)
    return it


def score_all(items: Iterable[Item], pass2_top_n: int = 20) -> list[Item]:
    """Two-pass scoring: cheap filter on all, smart rerank on top N."""
    # Pass 1: quick score everything
    scored: list[Item] = []
    for it in items:
        try:
            scored.append(_score_pass1(it))
        except Exception as e:
            it.raw_score = 0.0
            it.score = 0.0
            it.why_it_matters = f"(scoring failed: {e})"
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
