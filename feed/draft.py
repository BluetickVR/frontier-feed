"""Generate Twitter/LinkedIn posts from digest items or dossiers."""
from __future__ import annotations

from pathlib import Path

from feed.llm import chat, load_context
from feed.models import Item
from feed.state import load_item

ROOT = Path(__file__).resolve().parent.parent

_TWITTER_SYSTEM = """You write tweets for a founder/CTO in real estate tech who's deeply into AI.
Rules:
- Max 270 chars (leave room for a link)
- Sound like a person, not a brand. No hashtags. No emojis unless truly warranted.
- Lead with the insight, not "I just learned..." or "Check this out..."
- If there's a contrarian take or practical implication, lead with that.
- End with the URL (I'll append it).
Output ONLY the tweet text, nothing else."""

_LINKEDIN_SYSTEM = """You write LinkedIn posts for a founder/CTO (Anshul Padyal, PropViz/MagicBricks).
Rules:
- 150-250 words. Short paragraphs (2-3 sentences each).
- Start with a hook line that makes someone stop scrolling.
- Share a genuine insight or take — not a summary.
- Connect to real estate / enterprise SaaS where natural, but don't force it.
- End with a question or forward-looking statement.
- No hashtags. No emojis. No "I'm excited to share..."
- Sound thoughtful, not performative.
Output ONLY the post text, nothing else."""


def draft_tweet(item: Item) -> str:
    ctx = load_context()
    prompt = (
        f"Writer: {ctx['identity']['name']}, {ctx['identity']['role']}\n\n"
        f"Item to tweet about:\n"
        f"Title: {item.title}\n"
        f"URL: {item.url}\n"
        f"Summary: {(item.summary or '')[:500]}\n"
        f"Why it matters: {item.why_it_matters or ''}\n"
    )
    text = chat("synthesis", prompt, system=_TWITTER_SYSTEM, temperature=0.7, max_tokens=200)
    # ensure URL is included
    if item.url not in text:
        text = f"{text}\n\n{item.url}"
    return text


def draft_linkedin(item: Item, dossier_text: str | None = None) -> str:
    ctx = load_context()
    body = dossier_text or (item.summary or "")
    prompt = (
        f"Writer: {ctx['identity']['name']}, {ctx['identity']['role']}\n"
        f"Ambition: {ctx['identity'].get('ambition', ctx['identity'].get('goal', ''))}\n\n"
        f"Item:\n"
        f"Title: {item.title}\n"
        f"URL: {item.url}\n"
        f"Content: {body[:1500]}\n"
        f"Why it matters: {item.why_it_matters or ''}\n"
    )
    text = chat("synthesis", prompt, system=_LINKEDIN_SYSTEM, temperature=0.7, max_tokens=600)
    if item.url not in text:
        text = f"{text}\n\n{item.url}"
    return text


def draft_from_id(item_id: str, platform: str = "twitter") -> str | None:
    item = load_item(item_id)
    if not item:
        return None
    # check for dossier
    dossier_path = ROOT / "dossiers" / f"{item_id}.md"
    dossier_text = dossier_path.read_text() if dossier_path.exists() else None

    if platform == "twitter":
        return draft_tweet(item)
    elif platform == "linkedin":
        return draft_linkedin(item, dossier_text)
    return None
