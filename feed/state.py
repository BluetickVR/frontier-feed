from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Optional

import yaml

from feed.models import Item, Reaction

STATE_DIR = Path(__file__).resolve().parent.parent / "state"
POINTER_FILE = STATE_DIR / "knowledge_pointer.yaml"
REACTIONS_FILE = STATE_DIR / "reactions.jsonl"
WEIGHTS_FILE = STATE_DIR / "source_weights.yaml"
ITEMS_FILE = STATE_DIR / "items.jsonl"


def _ensure():
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    for f in (POINTER_FILE, WEIGHTS_FILE):
        if not f.exists():
            f.write_text("{}\n")
    for f in (REACTIONS_FILE, ITEMS_FILE):
        if not f.exists():
            f.touch()


# ---------- pointers ----------

def load_pointers() -> dict[str, datetime]:
    _ensure()
    raw = yaml.safe_load(POINTER_FILE.read_text()) or {}
    out: dict[str, datetime] = {}
    for k, v in raw.items():
        if isinstance(v, str):
            out[k] = datetime.fromisoformat(v.replace("Z", "+00:00"))
        elif isinstance(v, datetime):
            out[k] = v if v.tzinfo else v.replace(tzinfo=timezone.utc)
    return out


def save_pointer(source: str, when: datetime) -> None:
    _ensure()
    raw = yaml.safe_load(POINTER_FILE.read_text()) or {}
    raw[source] = when.astimezone(timezone.utc).isoformat()
    POINTER_FILE.write_text(yaml.safe_dump(raw, sort_keys=True))


def get_pointer(source: str) -> Optional[datetime]:
    return load_pointers().get(source)


# ---------- source weights (learned from reactions) ----------

def load_weights() -> dict[str, float]:
    _ensure()
    return yaml.safe_load(WEIGHTS_FILE.read_text()) or {}


def save_weights(w: dict[str, float]) -> None:
    _ensure()
    WEIGHTS_FILE.write_text(yaml.safe_dump(w, sort_keys=True))


def weight_for(source: str) -> float:
    return float(load_weights().get(source, 1.0))


# ---------- items log (everything we've ever seen) ----------

def log_items(items: Iterable[Item]) -> None:
    _ensure()
    with ITEMS_FILE.open("a") as f:
        for it in items:
            f.write(it.model_dump_json() + "\n")


def seen_item_ids() -> set[str]:
    _ensure()
    ids: set[str] = set()
    with ITEMS_FILE.open() as f:
        for line in f:
            if not line.strip():
                continue
            try:
                ids.add(json.loads(line)["id"])
            except Exception:
                continue
    return ids


def load_item(item_id: str) -> Optional[Item]:
    """Find an item by id — newest wins (we append, so read last match)."""
    _ensure()
    found: Optional[Item] = None
    with ITEMS_FILE.open() as f:
        for line in f:
            if not line.strip():
                continue
            try:
                d = json.loads(line)
                if d.get("id") == item_id:
                    found = Item.model_validate(d)
            except Exception:
                continue
    return found


# ---------- reactions ----------

def log_reaction(r: Reaction) -> None:
    _ensure()
    with REACTIONS_FILE.open("a") as f:
        f.write(r.model_dump_json() + "\n")


def load_reactions() -> list[Reaction]:
    _ensure()
    out: list[Reaction] = []
    with REACTIONS_FILE.open() as f:
        for line in f:
            if not line.strip():
                continue
            try:
                out.append(Reaction.model_validate_json(line))
            except Exception:
                continue
    return out


def reactions_since(when: datetime) -> list[Reaction]:
    when_utc = when.astimezone(timezone.utc)
    return [r for r in load_reactions() if r.at >= when_utc]


def reacted_item_ids() -> set[str]:
    """Ids of items that received any reaction — won't re-surface."""
    return {r.item_id for r in load_reactions()}


# ---------- retune ----------

def retune_weights(
    positive: float = 1.15,
    negative: float = 0.80,
    question: float = 1.05,
    floor: float = 0.3,
    cap: float = 2.0,
) -> dict[str, float]:
    """Apply reactions to source weights. Idempotent per reaction by virtue of
    the weight being recomputed from scratch every call."""
    _ensure()
    weights: dict[str, float] = {}
    # recompute from reactions
    from collections import Counter

    counts: dict[str, Counter] = {}
    for r in load_reactions():
        it = load_item(r.item_id)
        if not it:
            continue
        src = it.source
        counts.setdefault(src, Counter())[r.char] += 1
    for src, c in counts.items():
        w = 1.0
        w *= positive ** c.get("+", 0)
        w *= negative ** c.get("-", 0)
        w *= question ** c.get("?", 0)
        # "." is neutral
        weights[src] = max(floor, min(cap, w))
    save_weights(weights)
    return weights
