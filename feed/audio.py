"""Generate audio briefings from digest items using Edge TTS."""
from __future__ import annotations

import asyncio
import os
from datetime import datetime, timezone
from pathlib import Path

import edge_tts
import httpx

from feed.llm import chat, load_context
from feed.models import Item
from feed.state import seen_item_ids

ROOT = Path(__file__).resolve().parent.parent
AUDIO_DIR = ROOT / "site" / "audio"

VOICE = "en-IN-PrabhatNeural"  # Indian English male, natural

_SCRIPT_SYSTEM = """You write 3-minute audio briefing scripts for a busy CTO driving to work.
Rules:
- Conversational, like a smart colleague in the passenger seat
- Start with "Good morning Anshul, here's what matters today."
- Cover each item in 2-3 sentences: what it is, why it matters for PropViz
- Transition naturally between items ("Moving on...", "Also worth noting...", "The big one today...")
- End with "That's your briefing. Have a good one."
- No markdown, no bullets, no URLs — this will be spoken aloud
- Total: 400-500 words (about 3 minutes at speaking pace)"""


def _generate_script(items: list[Item]) -> str:
    ctx = load_context()
    items_text = "\n\n".join(
        f"[{it.source}] {it.title}\nScore: {it.score}\nWhy: {it.why_it_matters or ''}\nSummary: {(it.summary or '')[:200]}"
        for it in items[:10]
    )
    prompt = (
        f"Reader: {ctx['identity']['name']}, {ctx['identity']['role']}\n"
        f"Date: {datetime.now(timezone.utc).strftime('%A, %B %d, %Y')}\n\n"
        f"Today's top items (in priority order):\n{items_text}\n\n"
        f"Write the briefing script."
    )
    return chat("synthesis", prompt, system=_SCRIPT_SYSTEM, temperature=0.6, max_tokens=1200)


async def _tts(text: str, output_path: Path) -> None:
    communicate = edge_tts.Communicate(text, VOICE, rate="+5%")
    await communicate.save(str(output_path))


def _push_voice_to_telegram(audio_path: Path, caption: str = "") -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    if not token or not chat_id:
        return
    url = f"https://api.telegram.org/bot{token}/sendVoice"
    with open(audio_path, "rb") as f:
        r = httpx.post(
            url,
            data={"chat_id": chat_id, "caption": caption[:1024]},
            files={"voice": (audio_path.name, f, "audio/mpeg")},
            timeout=60,
        )
    r.raise_for_status()


def generate_briefing(items: list[Item], slot: str = "morning") -> dict:
    """Generate audio briefing from scored items, push to Telegram."""
    if not items:
        return {"ok": False, "reason": "no items"}

    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    ymd = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Generate script
    script = _generate_script(items)

    # Save script
    script_path = AUDIO_DIR / f"{ymd}-{slot}.txt"
    script_path.write_text(script)

    # Generate audio
    audio_path = AUDIO_DIR / f"{ymd}-{slot}.mp3"
    asyncio.run(_tts(script, audio_path))

    # Push to Telegram
    size_mb = audio_path.stat().st_size / 1024 / 1024
    try:
        _push_voice_to_telegram(
            audio_path,
            caption=f"🎧 {slot.title()} briefing — {len(items)} items, {size_mb:.1f}MB"
        )
    except Exception as e:
        print(f"[audio] telegram push failed: {e}")

    return {
        "ok": True,
        "script_path": str(script_path),
        "audio_path": str(audio_path),
        "size_mb": round(size_mb, 1),
        "items": len(items),
    }
