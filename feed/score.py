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


_PASS1_SYSTEM = """You STRICTLY score items for a founder building the #1 real estate tech company using AI + 3D.

CALIBRATION (follow these EXACTLY):
0.95: "Gaussian splatting renders 3D property tours at 60fps in browser" — direct product capability
0.90: "New voice AI model with 200ms latency, supports Hindi" — direct product capability
0.85: "Three.js 2.0 released with WebGPU support" — his core 3D stack
0.80: "Agent SDK for multi-step workflows with tool use" — makes his team faster
0.70: "Claude Code adds MCP support for databases" — dev velocity tool
0.60: "New foundation model beats GPT-5 on coding" — useful but generic
0.50: "AI startup raises $50M for developer tools" — news, not actionable
0.40: "Yet another RAG framework" — crowded space, generic
0.30: "AI ethics paper on bias in hiring" — not relevant
0.20: "Generic agent framework #47 with no differentiation" — noise
0.10: "Crypto AI token launch" — irrelevant

MOST items should score 0.3-0.6. Only truly exceptional items score 0.8+.
If you score more than 2 items above 0.8 in a batch, you're being too generous.

Return JSON: {"score": float 0-1, "why": "<12 words max>"}
Output ONLY valid JSON."""


_PASS2_SYSTEM = """Re-rank this item for Anshul Padyal, CTO building the #1 real estate tech company.

His MOAT is AI + 3D applied to property sales. Company: PropViz (MagicBricks/Times Group).
Products: VR tours, 3D maps, AI voice caller (Ultravox), WhatsApp AI bot, inventory platform.
Stack: React, Node, Python, Ultravox, Meta WhatsApp API, WebSockets, AWS, Three.js.
Team: 8 devs. Every tool that makes them 10x faster matters.

Score this item on ONE question: "If Anshul ignores this, will a competitor use it to beat him?"

CALIBRATION:
0.95: A 3D rendering breakthrough that makes virtual property tours indistinguishable from photos
0.85: A voice AI model that handles Hindi/English code-switching with 150ms latency
0.75: A tool that lets his 8-dev team ship like a 40-dev team
0.60: A new model release that's better at coding tasks
0.45: An interesting AI technique with no clear real estate application
0.30: Generic developer tool trending on GitHub
0.15: AI news with no actionable takeaway

BE BRUTAL. Most items are 0.3-0.5. The world's #1 company isn't built on generic AI repos.

Return JSON: {"score": float 0-1, "why": "<18 words — HOW specifically this applies to his 3D/voice/sales business>"}
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
    prompt = (
        f"{_context_blurb()}\n\n"
        f"Item: [{it.source}] {it.title}\n"
        f"URL: {it.url}\n"
        f"Summary: {body}\n"
    )
    raw = _chat_with_fallback("classify", prompt, system=_PASS1_SYSTEM,
                              temperature=0.1, max_tokens=120)
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
                              temperature=0.2, max_tokens=150)
    score, why = _parse(raw)
    if why:
        it.why_it_matters = why
    blended = (score * 0.7) + (it.raw_score * 0.3)
    it.score = round(blended * weight_for(it.source), 3)
    return it


def score_all(items: Iterable[Item], pass2_top_n: int = 20) -> list[Item]:
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
