"""Post digest items to Telegram, one message per item."""
from __future__ import annotations

import html
import os
import time
from typing import Iterable

import httpx

from feed.models import Item

_API = "https://api.telegram.org/bot{token}/{method}"

_REPLY_LEGEND = "reply: <code>.</code> read · <code>?</code> dig · <code>+</code> more like this · <code>-</code> less"


def _token() -> str:
    t = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    if not t:
        raise RuntimeError("TELEGRAM_BOT_TOKEN not set")
    return t


def _chat_id() -> str:
    c = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    if not c:
        raise RuntimeError("TELEGRAM_CHAT_ID not set")
    return c


def _send(method: str, payload: dict) -> dict:
    url = _API.format(token=_token(), method=method)
    r = httpx.post(url, json=payload, timeout=20)
    r.raise_for_status()
    body = r.json()
    if not body.get("ok"):
        raise RuntimeError(f"telegram {method} failed: {body}")
    return body["result"]


def _fmt_item(it: Item, tag: str = "") -> str:
    title = html.escape(it.title)
    source = html.escape(it.source)
    why = html.escape(it.why_it_matters or "")
    url = html.escape(it.url)
    lines = []
    if tag:
        lines.append(f"<b>{html.escape(tag)}</b>")
    lines.append(f"🔹 <b>[{source}]</b> {title}")
    if why:
        lines.append(f"<i>{why}</i>")
    lines.append(f'<a href="{url}">{url}</a>')
    lines.append(f"<code>{it.id}</code>   {_REPLY_LEGEND}")
    return "\n".join(lines)


def send_text(text: str, disable_preview: bool = False) -> dict:
    return _send(
        "sendMessage",
        {
            "chat_id": _chat_id(),
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": disable_preview,
        },
    )


def push_items(items: Iterable[Item], header: str | None = None) -> list[Item]:
    items = list(items)
    if header:
        send_text(f"<b>{html.escape(header)}</b>", disable_preview=True)
    pushed: list[Item] = []
    for it in items:
        try:
            res = _send(
                "sendMessage",
                {
                    "chat_id": _chat_id(),
                    "text": _fmt_item(it),
                    "parse_mode": "HTML",
                    "disable_web_page_preview": False,
                },
            )
            it.tg_message_id = int(res.get("message_id") or 0)
            it.status = "pushed"
            from datetime import datetime, timezone
            it.pushed_at = datetime.now(timezone.utc)
            pushed.append(it)
            time.sleep(0.4)  # gentle throttle
        except Exception as e:
            send_text(f"(push error for {it.id}: {html.escape(str(e))})")
    return pushed


def push_dossier(item: Item, briefing_md: str) -> None:
    # keep under Telegram's 4096-char limit
    body = briefing_md.strip()
    if len(body) > 3500:
        body = body[:3500] + "\n\n…(truncated)"
    send_text(
        f"📎 <b>Follow-up: {html.escape(item.title)}</b>\n\n{html.escape(body)}\n\n"
        f'<a href="{html.escape(item.url)}">original</a>',
        disable_preview=True,
    )
