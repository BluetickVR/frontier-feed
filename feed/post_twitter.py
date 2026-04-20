"""Post tweets using Twitter's internal API (same cookies as fetcher)."""
from __future__ import annotations

import json
import os
import uuid

import httpx


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


def post_tweet(text: str) -> dict:
    """Post a tweet. Returns {"id": "...", "text": "..."}."""
    payload = {
        "variables": {
            "tweet_text": text,
            "dark_request": False,
            "media": {"media_entities": [], "possibly_sensitive": False},
            "semantic_annotation_ids": [],
        },
        "features": {
            "communities_web_enable_tweet_community_results_fetch": True,
            "c9s_tweet_anatomy_moderator_badge_enabled": True,
            "responsive_web_edit_tweet_api_enabled": True,
            "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
            "view_counts_everywhere_api_enabled": True,
            "longform_notetweets_consumption_enabled": True,
            "responsive_web_twitter_article_tweet_consumption_enabled": True,
            "tweet_awards_web_tipping_enabled": False,
            "creator_subscriptions_quote_tweet_preview_enabled": False,
            "longform_notetweets_rich_text_read_enabled": True,
            "longform_notetweets_inline_media_enabled": True,
            "articles_preview_enabled": True,
            "rweb_video_timestamps_enabled": True,
            "rweb_tipjar_consumption_enabled": True,
            "responsive_web_graphql_exclude_directive_enabled": True,
            "verified_phone_label_enabled": False,
            "freedom_of_speech_not_reach_fetch_enabled": True,
            "standardized_nudges_misinfo": True,
            "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True,
            "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
            "responsive_web_graphql_timeline_navigation_enabled": True,
            "responsive_web_enhance_cards_enabled": False,
        },
        "queryId": "znCTAKn0JnMXTSP3RjEbHA",
    }

    r = httpx.post(
        "https://x.com/i/api/graphql/znCTAKn0JnMXTSP3RjEbHA/CreateTweet",
        headers=_headers(),
        json=payload,
        timeout=20,
    )
    r.raise_for_status()
    data = r.json()

    try:
        result = data["data"]["create_tweet"]["tweet_results"]["result"]
        return {
            "id": result["rest_id"],
            "text": result.get("legacy", {}).get("full_text", text),
            "url": f"https://x.com/i/status/{result['rest_id']}",
        }
    except (KeyError, TypeError):
        return {"id": "", "text": text, "raw": str(data)[:500]}
