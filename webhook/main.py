"""Telegram webhook receiver.

Responsibilities:
- Accept Telegram Update POSTs at /webhook/<secret>
- Extract the reply (a single char from {., ?, +, -} or free text) and the
  item_id from the replied-to message (stored as the last code block)
- Append a Reaction JSON line to reactions.jsonl in the frontier-feed GitHub
  repo via the GitHub Contents API
- Respond 200 OK quickly so Telegram doesn't retry

Env vars (Fly secrets):
  TELEGRAM_WEBHOOK_SECRET  random string, used in the URL path
  GITHUB_TOKEN             PAT with repo scope
  GITHUB_REPO              owner/repo, e.g. anshulpadyal/frontier-feed
  GITHUB_BRANCH            default: main
  TELEGRAM_BOT_TOKEN       used only to verify incoming chat_id matches TELEGRAM_CHAT_ID
  TELEGRAM_CHAT_ID         your personal chat id (drop everything else)
"""
from __future__ import annotations

import base64
import json
import os
import re
import time
from datetime import datetime, timezone

import httpx
from fastapi import FastAPI, HTTPException, Request

app = FastAPI()

WEBHOOK_SECRET = os.environ.get("TELEGRAM_WEBHOOK_SECRET", "").strip()
GH_TOKEN = os.environ.get("GITHUB_TOKEN", "").strip()
GH_REPO = os.environ.get("GITHUB_REPO", "").strip()
GH_BRANCH = os.environ.get("GITHUB_BRANCH", "main").strip()
TG_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
TG_BOT = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()

REACTIONS_PATH = "state/reactions.jsonl"

VALID_CHARS = {".", "?", "+", "-"}

# item_id in pushed messages appears as a <code>id</code> block:
# id pattern from models.stable_id: "<source>-<12-hex>"
_ID_RE = re.compile(r"([a-z0-9_\-]{1,40}-[a-f0-9]{12})")


@app.get("/healthz")
def healthz():
    return {"ok": True, "ts": datetime.now(timezone.utc).isoformat()}


def _extract_item_id(replied_text: str) -> str | None:
    if not replied_text:
        return None
    m = _ID_RE.search(replied_text)
    return m.group(1) if m else None


def _parse_reaction(text: str) -> tuple[str, str | None]:
    """Return (char, free_text_or_none)."""
    t = text.strip()
    if not t:
        return "", None
    # single-char shortcuts
    if t in VALID_CHARS:
        return t, None
    # leading char + note: "? tell me more about ..."
    first = t[0]
    if first in VALID_CHARS and (len(t) == 1 or t[1] in (" ", "\n")):
        note = t[1:].strip() or None
        return first, note
    # free-form text treated as a note (default to ".")
    return ".", t


def _gh_get_sha() -> tuple[str | None, str]:
    """Return (sha, current_content_str). current_content is '' if file absent."""
    url = f"https://api.github.com/repos/{GH_REPO}/contents/{REACTIONS_PATH}?ref={GH_BRANCH}"
    h = {"Authorization": f"Bearer {GH_TOKEN}", "Accept": "application/vnd.github+json"}
    r = httpx.get(url, headers=h, timeout=15)
    if r.status_code == 404:
        return None, ""
    r.raise_for_status()
    j = r.json()
    content = base64.b64decode(j["content"]).decode("utf-8", errors="replace")
    return j["sha"], content


def _gh_put(content: str, sha: str | None, message: str) -> None:
    url = f"https://api.github.com/repos/{GH_REPO}/contents/{REACTIONS_PATH}"
    h = {"Authorization": f"Bearer {GH_TOKEN}", "Accept": "application/vnd.github+json"}
    payload = {
        "message": message,
        "branch": GH_BRANCH,
        "content": base64.b64encode(content.encode("utf-8")).decode("ascii"),
    }
    if sha:
        payload["sha"] = sha
    r = httpx.put(url, headers=h, json=payload, timeout=20)
    r.raise_for_status()


def _append_reaction_to_repo(line: str, retries: int = 3) -> None:
    for attempt in range(retries):
        sha, cur = _gh_get_sha()
        new_content = cur + line + "\n"
        try:
            _gh_put(new_content, sha, f"reaction: {line[:80]}")
            return
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 409 and attempt < retries - 1:
                time.sleep(0.5 * (attempt + 1))
                continue
            raise


def _tg_reply(chat_id: int, text: str) -> None:
    if not TG_BOT:
        return
    try:
        httpx.post(
            f"https://api.telegram.org/bot{TG_BOT}/sendMessage",
            json={"chat_id": chat_id, "text": text},
            timeout=10,
        )
    except Exception:
        pass


@app.post("/webhook/{secret}")
async def webhook(secret: str, request: Request):
    if not WEBHOOK_SECRET or secret != WEBHOOK_SECRET:
        raise HTTPException(status_code=404)

    try:
        update = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="bad json")

    msg = update.get("message") or update.get("edited_message") or {}
    chat = msg.get("chat") or {}
    chat_id = chat.get("id")
    text = (msg.get("text") or "").strip()

    # drop anything not from our owner
    if TG_CHAT_ID and str(chat_id) != TG_CHAT_ID:
        return {"ok": True, "dropped": "unauthorized_chat"}

    # must be a reply to a bot message
    reply_to = msg.get("reply_to_message") or {}
    replied_text = reply_to.get("text") or reply_to.get("caption") or ""
    item_id = _extract_item_id(replied_text)

    if not item_id:
        # maybe a command or plain chat — ignore silently
        return {"ok": True, "dropped": "no_item_id"}

    char, note = _parse_reaction(text)
    if char not in VALID_CHARS:
        _tg_reply(chat_id, "couldn't parse reaction — use . ? + - (optionally followed by a note)")
        return {"ok": True, "dropped": "bad_char"}

    reaction = {
        "item_id": item_id,
        "char": char,
        "text": note,
        "at": datetime.now(timezone.utc).isoformat(),
        "tg_message_id": msg.get("message_id"),
    }
    line = json.dumps(reaction, separators=(",", ":"))

    try:
        _append_reaction_to_repo(line)
    except Exception as e:
        _tg_reply(chat_id, f"⚠️ failed to save reaction: {e}")
        return {"ok": False, "error": str(e)}

    _tg_reply(chat_id, f"✓ {char} saved for {item_id}")
    return {"ok": True, "saved": reaction}
