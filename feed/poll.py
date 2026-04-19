"""Poll Telegram getUpdates for reactions, save to state."""
from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

import httpx

from feed.models import Reaction
from feed.state import log_reaction

ROOT = Path(__file__).resolve().parent.parent
OFFSET_FILE = ROOT / "state" / "tg_offset.txt"

_ID_RE = re.compile(r"([a-z0-9_\-]{1,40}-[a-f0-9]{12})")
VALID_CHARS = {".", "?", "+", "-"}


def _token() -> str:
    return os.environ["TELEGRAM_BOT_TOKEN"]


def _chat_id() -> str:
    return os.environ["TELEGRAM_CHAT_ID"]


def _load_offset() -> int:
    if OFFSET_FILE.exists():
        try:
            return int(OFFSET_FILE.read_text().strip())
        except ValueError:
            pass
    return 0


def _save_offset(offset: int) -> None:
    OFFSET_FILE.parent.mkdir(parents=True, exist_ok=True)
    OFFSET_FILE.write_text(str(offset))


def _get_updates(offset: int) -> list[dict]:
    url = f"https://api.telegram.org/bot{_token()}/getUpdates"
    params = {"timeout": 0, "allowed_updates": '["message"]'}
    if offset:
        params["offset"] = offset
    r = httpx.get(url, params=params, timeout=15)
    r.raise_for_status()
    return r.json().get("result", [])


def _reply_text(chat_id: int, text: str) -> None:
    try:
        httpx.post(
            f"https://api.telegram.org/bot{_token()}/sendMessage",
            json={"chat_id": chat_id, "text": text},
            timeout=10,
        )
    except Exception:
        pass


def _extract_item_id(text: str) -> str | None:
    m = _ID_RE.search(text or "")
    return m.group(1) if m else None


def _parse_reaction(text: str) -> tuple[str, str | None]:
    t = text.strip()
    if not t:
        return "", None
    if t in VALID_CHARS:
        return t, None
    first = t[0]
    if first in VALID_CHARS and (len(t) == 1 or t[1] in (" ", "\n")):
        return first, t[1:].strip() or None
    return ".", t


def run_poll() -> dict:
    offset = _load_offset()
    updates = _get_updates(offset)
    my_chat = _chat_id()
    processed = 0
    skipped = 0
    max_update_id = offset

    for u in updates:
        uid = u.get("update_id", 0)
        if uid > max_update_id:
            max_update_id = uid

        msg = u.get("message") or {}
        chat = msg.get("chat") or {}
        chat_id = chat.get("id")
        text = (msg.get("text") or "").strip()

        if str(chat_id) != my_chat:
            skipped += 1
            continue

        reply_to = msg.get("reply_to_message") or {}
        replied_text = reply_to.get("text") or reply_to.get("caption") or ""
        item_id = _extract_item_id(replied_text)

        if not item_id:
            skipped += 1
            continue

        char, note = _parse_reaction(text)
        if char not in VALID_CHARS:
            _reply_text(chat_id, "use . ? + - (optionally followed by a note)")
            skipped += 1
            continue

        r = Reaction(
            item_id=item_id,
            char=char,
            text=note,
            at=datetime.now(timezone.utc),
            tg_message_id=msg.get("message_id"),
        )
        log_reaction(r)
        _reply_text(chat_id, f"✓ {char} saved for {item_id}")
        processed += 1

    if updates:
        _save_offset(max_update_id + 1)

    return {"updates": len(updates), "processed": processed, "skipped": skipped}
