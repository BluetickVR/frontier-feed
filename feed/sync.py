"""Push state files to GitHub via the Contents API. No git push needed."""
from __future__ import annotations

import base64
import os
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent
STATE_DIR = ROOT / "state"
DIGESTS_DIR = ROOT / "digests"
JOURNALS_DIR = ROOT / "journals"
DOSSIERS_DIR = ROOT / "dossiers"
STRATEGIES_DIR = ROOT / "strategies"


def _token() -> str:
    t = os.environ.get("GITHUB_TOKEN", "").strip()
    if not t:
        raise RuntimeError("GITHUB_TOKEN not set")
    return t


def _repo() -> str:
    return os.environ.get("GITHUB_REPO", "BluetickVR/frontier-feed").strip()


def _branch() -> str:
    return os.environ.get("GITHUB_BRANCH", "main").strip()


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {_token()}",
        "Accept": "application/vnd.github+json",
    }


def _get_sha(path: str) -> str | None:
    url = f"https://api.github.com/repos/{_repo()}/contents/{path}?ref={_branch()}"
    r = httpx.get(url, headers=_headers(), timeout=15)
    if r.status_code == 404:
        return None
    r.raise_for_status()
    return r.json().get("sha")


def _put_file(path: str, content: bytes, message: str) -> bool:
    url = f"https://api.github.com/repos/{_repo()}/contents/{path}"
    sha = _get_sha(path)
    payload = {
        "message": message,
        "branch": _branch(),
        "content": base64.b64encode(content).decode("ascii"),
    }
    if sha:
        payload["sha"] = sha
    r = httpx.put(url, headers=_headers(), json=payload, timeout=20)
    if r.status_code in (200, 201):
        return True
    print(f"[sync] PUT {path} failed: {r.status_code} {r.text[:200]}")
    return False


def sync_state() -> dict:
    """Push all state/ files + today's digest/journal/dossier/strategy files."""
    pushed = 0
    failed = 0

    # state files — always push
    for f in STATE_DIR.glob("*"):
        if f.is_file() and f.name != ".gitkeep":
            rel = f"state/{f.name}"
            ok = _put_file(rel, f.read_bytes(), f"sync: {rel}")
            if ok:
                pushed += 1
            else:
                failed += 1

    # today's output files — push if they exist
    from datetime import datetime, timezone
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    for dir_path, prefix in [
        (DIGESTS_DIR, "digests"),
        (JOURNALS_DIR, "journals"),
        (DOSSIERS_DIR, "dossiers"),
        (STRATEGIES_DIR, "strategies"),
    ]:
        if not dir_path.exists():
            continue
        for f in dir_path.glob("*"):
            if f.is_file() and today in f.name:
                rel = f"{prefix}/{f.name}"
                ok = _put_file(rel, f.read_bytes(), f"sync: {rel}")
                if ok:
                    pushed += 1
                else:
                    failed += 1

    return {"pushed": pushed, "failed": failed}
