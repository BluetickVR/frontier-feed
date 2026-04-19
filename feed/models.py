from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Literal, Optional

from pydantic import BaseModel, Field


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def stable_id(source: str, url: str) -> str:
    """Deterministic item id from source + url."""
    h = hashlib.sha1(f"{source}:{url}".encode()).hexdigest()[:12]
    return f"{source}-{h}"


ReactionChar = Literal[".", "?", "+", "-", "!", "p"]
ItemStatus = Literal["pending", "pushed", "read", "dug", "dismissed"]


class Item(BaseModel):
    id: str
    source: str
    url: str
    title: str
    summary: Optional[str] = None
    why_it_matters: Optional[str] = None
    raw_score: float = 0.0
    score: float = 0.0                    # post-weight
    published_at: Optional[datetime] = None
    first_seen: datetime = Field(default_factory=_utcnow)
    pushed_at: Optional[datetime] = None
    status: ItemStatus = "pending"
    tg_message_id: Optional[int] = None
    extra: dict = Field(default_factory=dict)

    @classmethod
    def new(cls, source: str, url: str, title: str, **kw) -> "Item":
        return cls(id=stable_id(source, url), source=source, url=url, title=title, **kw)


class Reaction(BaseModel):
    item_id: str
    char: ReactionChar
    text: Optional[str] = None           # free-form note if user sent more than one char
    at: datetime = Field(default_factory=_utcnow)
    tg_message_id: Optional[int] = None
