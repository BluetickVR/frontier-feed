"""Provider-agnostic LLM client. Routes via config.yaml."""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Optional

import yaml
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")


@lru_cache
def load_config() -> dict:
    return yaml.safe_load((ROOT / "config.yaml").read_text())


@lru_cache
def load_context() -> dict:
    return yaml.safe_load((ROOT / "context.yaml").read_text())


def provider_for(task: str) -> str:
    """task ∈ {summarize, classify, rank, synthesis, embedding}"""
    cfg = load_config()
    return cfg["routes"][task]


def _groq_client():
    from groq import Groq

    key = os.environ.get("GROQ_API_KEY", "").strip()
    if not key:
        raise RuntimeError("GROQ_API_KEY not set")
    return Groq(api_key=key)


def _gemini_chat(model_name: str, prompt: str, system: str | None = None,
                 temperature: float = 0.3, max_tokens: int = 512) -> str:
    """Call Gemini via REST API directly — no SDK needed."""
    import httpx

    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not key:
        raise RuntimeError("GEMINI_API_KEY not set")

    if not model_name.startswith("models/"):
        model_name = f"models/{model_name}"
    url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent?key={key}"

    contents = []
    if system:
        contents.append({"role": "user", "parts": [{"text": system + "\n\n" + prompt}]})
    else:
        contents.append({"role": "user", "parts": [{"text": prompt}]})

    body = {
        "contents": contents,
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": max_tokens,
            "thinkingConfig": {"thinkingBudget": 0},
        },
    }

    r = httpx.post(url, json=body, timeout=30)
    r.raise_for_status()
    data = r.json()
    try:
        parts = data["candidates"][0]["content"]["parts"]
        return parts[-1]["text"].strip()
    except (KeyError, IndexError):
        return ""


def chat(task: str, prompt: str, system: Optional[str] = None, temperature: float = 0.3,
         max_tokens: int = 512) -> str:
    """Send a chat completion. Returns plain text."""
    cfg = load_config()
    prov = provider_for(task)

    if prov == "groq":
        g = cfg["providers"]["groq"]["models"]
        model = g.get(task) or g.get("summarize")
        client = _groq_client()
        msgs = []
        if system:
            msgs.append({"role": "system", "content": system})
        msgs.append({"role": "user", "content": prompt})
        r = client.chat.completions.create(
            model=model, messages=msgs, temperature=temperature, max_tokens=max_tokens
        )
        return (r.choices[0].message.content or "").strip()

    if prov == "gemini":
        model_name = cfg["providers"]["gemini"]["models"].get("fallback_chat", "gemini-2.0-flash")
        return _gemini_chat(model_name, prompt, system=system,
                           temperature=temperature, max_tokens=max_tokens)

    if prov == "anthropic":
        import anthropic
        key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
        if not key:
            raise RuntimeError("ANTHROPIC_API_KEY not set")
        client = anthropic.Anthropic(api_key=key)
        model = cfg["providers"]["anthropic"]["models"].get("synthesis", "claude-sonnet-4-6")
        r = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system or "",
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
        )
        return r.content[0].text.strip()

    raise RuntimeError(f"Unknown provider for task {task!r}: {prov}")
