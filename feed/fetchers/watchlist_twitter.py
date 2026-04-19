"""Fetch recent tweets from watchlist handles via Twitter's internal API.

Uses the authenticated user's session cookies (auth_token + ct0) to access
Twitter's GraphQL UserTweets endpoint — the same one the browser uses.

Env vars:
  TWITTER_AUTH_TOKEN  — the `auth_token` cookie from x.com
  TWITTER_CT0        — the `ct0` cookie from x.com (CSRF token)
"""
from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from typing import Iterable, Iterator

import httpx

from feed.fetchers.base import BaseFetcher
from feed.llm import load_context
from feed.models import Item

_GRAPHQL_URL = "https://x.com/i/api/graphql"

_FEATURES = {
    "rweb_tipjar_consumption_enabled": True,
    "responsive_web_graphql_exclude_directive_enabled": True,
    "verified_phone_label_enabled": False,
    "creator_subscriptions_tweet_preview_api_enabled": True,
    "responsive_web_graphql_timeline_navigation_enabled": True,
    "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
    "communities_web_enable_tweet_community_results_fetch": True,
    "c9s_tweet_anatomy_moderator_badge_enabled": True,
    "articles_preview_enabled": True,
    "responsive_web_edit_tweet_api_enabled": True,
    "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
    "view_counts_everywhere_api_enabled": True,
    "longform_notetweets_consumption_enabled": True,
    "responsive_web_twitter_article_tweet_consumption_enabled": True,
    "tweet_awards_web_tipping_enabled": False,
    "creator_subscriptions_quote_tweet_preview_enabled": False,
    "freedom_of_speech_not_reach_fetch_enabled": True,
    "standardized_nudges_misinfo": True,
    "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True,
    "rweb_video_timestamps_enabled": True,
    "longform_notetweets_rich_text_read_enabled": True,
    "longform_notetweets_inline_media_enabled": True,
    "responsive_web_enhance_cards_enabled": False,
}


def _headers() -> dict:
    auth = os.environ.get("TWITTER_AUTH_TOKEN", "").strip()
    ct0 = os.environ.get("TWITTER_CT0", "").strip()
    if not auth or not ct0:
        raise RuntimeError("TWITTER_AUTH_TOKEN and TWITTER_CT0 must be set")
    return {
        "Authorization": "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA",
        "Cookie": f"auth_token={auth}; ct0={ct0}",
        "X-Csrf-Token": ct0,
        "X-Twitter-Active-User": "yes",
        "X-Twitter-Auth-Type": "OAuth2Session",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Content-Type": "application/json",
        "Referer": "https://x.com/",
    }


def _user_id_by_screen_name(handle: str, headers: dict) -> str | None:
    """Resolve @handle to numeric user ID."""
    variables = {"screen_name": handle, "withSafetyModeUserFields": True}
    params = {
        "variables": json.dumps(variables),
        "features": json.dumps({
            "hidden_profile_subscriptions_enabled": True,
            "rweb_tipjar_consumption_enabled": True,
            "responsive_web_graphql_exclude_directive_enabled": True,
            "verified_phone_label_enabled": False,
            "highlights_tweets_tab_ui_enabled": True,
            "responsive_web_twitter_article_tweet_consumption_enabled": True,
            "creator_subscriptions_tweet_preview_api_enabled": True,
            "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
            "responsive_web_graphql_timeline_navigation_enabled": True,
        }),
    }
    try:
        r = httpx.get(
            f"{_GRAPHQL_URL}/laYnJPCAcVo0o6pzcnlVxQ/UserByScreenName",
            headers=headers, params=params, timeout=15,
        )
        r.raise_for_status()
        data = r.json()
        return data["data"]["user"]["result"]["rest_id"]
    except Exception:
        return None


def _user_tweets(user_id: str, headers: dict, count: int = 20) -> list[dict]:
    """Fetch recent tweets for a user."""
    variables = {
        "userId": user_id,
        "count": count,
        "includePromotedContent": False,
        "withQuickPromoteEligibilityTweetFields": False,
        "withVoice": False,
        "withV2Timeline": True,
    }
    params = {
        "variables": json.dumps(variables),
        "features": json.dumps(_FEATURES),
    }
    try:
        r = httpx.get(
            f"{_GRAPHQL_URL}/E3opETHurmVJflFsUBVuUQ/UserTweets",
            headers=headers, params=params, timeout=15,
        )
        r.raise_for_status()
        return _extract_tweets(r.json())
    except Exception:
        return []


def _extract_tweets(data: dict) -> list[dict]:
    """Pull tweet objects out of Twitter's nested timeline response."""
    tweets: list[dict] = []
    try:
        instructions = (
            data.get("data", {})
            .get("user", {})
            .get("result", {})
            .get("timeline_v2", {})
            .get("timeline", {})
            .get("instructions", [])
        )
        for inst in instructions:
            entries = inst.get("entries", [])
            for entry in entries:
                content = entry.get("content", {})
                item_content = content.get("itemContent", {})
                result = item_content.get("tweet_results", {}).get("result", {})
                legacy = result.get("legacy", {})
                if legacy.get("full_text"):
                    core = result.get("core", {}).get("user_results", {}).get("result", {})
                    user_legacy = core.get("legacy", {})
                    tweets.append({
                        "id": legacy.get("id_str", ""),
                        "text": legacy["full_text"],
                        "created_at": legacy.get("created_at", ""),
                        "handle": user_legacy.get("screen_name", ""),
                        "name": user_legacy.get("name", ""),
                        "retweet_count": legacy.get("retweet_count", 0),
                        "favorite_count": legacy.get("favorite_count", 0),
                        "is_retweet": legacy["full_text"].startswith("RT @"),
                    })
    except Exception:
        pass
    return tweets


_AI_KEYWORDS = re.compile(
    r"\b(ai|llm|gpt|claude|gemini|agent|rag|mcp|transformer|diffusion|"
    r"fine.?tun|embed|vector|prompt|inference|train|model|neural|"
    r"langchain|llamaindex|cursor|copilot|anthropic|openai|deepseek|"
    r"mistral|hugging.?face|ollama|mlx|vllm|gguf|lora|rlhf|"
    r"tool.?use|function.?call|retrieval|benchmark|eval)\b",
    re.IGNORECASE,
)


def _is_ai_related(text: str) -> bool:
    return bool(_AI_KEYWORDS.search(text))


def _parse_twitter_date(s: str) -> datetime | None:
    try:
        return datetime.strptime(s, "%a %b %d %H:%M:%S %z %Y")
    except Exception:
        return None


class WatchlistTwitterFetcher(BaseFetcher):
    name = "watchlist_twitter"

    def _handles(self) -> list[str]:
        ctx = load_context()
        return ctx.get("watchlist", {}).get("research_and_builders", [])

    def fetch(self) -> Iterable[Item]:
        headers = _headers()
        handles = self._handles()
        max_per_user = int(self.cfg.get("max_tweets_per_user", 10))
        max_total = int(self.cfg.get("max_items_per_run", 30))
        items: list[Item] = []

        for handle in handles:
            # strip comments from yaml values like "karpathy  # Andrej"
            handle = handle.split("#")[0].strip().lstrip("@")
            if not handle:
                continue

            uid = _user_id_by_screen_name(handle, headers)
            if not uid:
                print(f"[watchlist] could not resolve @{handle}")
                continue

            tweets = _user_tweets(uid, headers, count=max_per_user)
            for tw in tweets:
                if tw["is_retweet"]:
                    continue
                text = tw["text"]
                if not _is_ai_related(text):
                    continue

                url = f"https://x.com/{handle}/status/{tw['id']}"
                published = _parse_twitter_date(tw["created_at"])
                engagement = tw["retweet_count"] + tw["favorite_count"]

                it = Item.new(
                    source=self.name,
                    url=url,
                    title=f"@{handle}: {text[:120]}{'...' if len(text) > 120 else ''}",
                    summary=text[:500],
                    published_at=published,
                    extra={
                        "handle": handle,
                        "name": tw["name"],
                        "engagement": engagement,
                        "retweets": tw["retweet_count"],
                        "likes": tw["favorite_count"],
                    },
                )
                items.append(it)

        # sort by engagement, cap total
        items.sort(key=lambda x: x.extra.get("engagement", 0), reverse=True)
        return items[:max_total]
