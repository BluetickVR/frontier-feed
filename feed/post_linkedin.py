"""Post to LinkedIn using session cookie."""
from __future__ import annotations

import json
import os
import re

import httpx


def _cookie() -> str:
    c = os.environ.get("LINKEDIN_COOKIE", "").strip()
    if not c:
        raise RuntimeError("LINKEDIN_COOKIE not set")
    return c


def _get_csrf(cookie: str) -> str:
    """Extract CSRF token from the li_at cookie — it's the JSESSIONID's value
    wrapped in quotes. We need to fetch the page first to get it."""
    headers = {
        "Cookie": f"li_at={cookie}",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    }
    r = httpx.get("https://www.linkedin.com/feed/", headers=headers, timeout=15, follow_redirects=True)
    # extract JSESSIONID from response cookies
    for c in r.cookies.jar:
        if c.name == "JSESSIONID":
            return c.value.strip('"')
    # fallback: try from set-cookie header
    for v in r.headers.get_list("set-cookie"):
        if "JSESSIONID" in v:
            m = re.search(r'JSESSIONID="?([^";]+)', v)
            if m:
                return m.group(1)
    raise RuntimeError("Could not extract LinkedIn CSRF token")


def post_linkedin(text: str) -> dict:
    """Post a text update to LinkedIn. Returns post metadata."""
    cookie = _cookie()
    csrf = _get_csrf(cookie)

    headers = {
        "Cookie": f"li_at={cookie}; JSESSIONID=\"{csrf}\"",
        "Csrf-Token": csrf,
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0",
    }

    payload = {
        "distribution": {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": [],
        },
        "commentary": text,
        "visibility": "PUBLIC",
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False,
    }

    r = httpx.post(
        "https://www.linkedin.com/voyager/api/contentcreation/normShares",
        headers=headers,
        json=payload,
        timeout=20,
    )

    if r.status_code in (200, 201):
        return {"ok": True, "status": r.status_code, "text_preview": text[:100]}
    else:
        return {"ok": False, "status": r.status_code, "error": r.text[:300]}
