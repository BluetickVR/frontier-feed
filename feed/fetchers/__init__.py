from feed.fetchers.base import BaseFetcher
from feed.fetchers.github_trending import GitHubTrendingFetcher
from feed.fetchers.watchlist_twitter import WatchlistTwitterFetcher

REGISTRY: dict[str, type[BaseFetcher]] = {
    "github_trending": GitHubTrendingFetcher,
    "watchlist_twitter": WatchlistTwitterFetcher,
}


def build_fetcher(name: str, cfg: dict) -> BaseFetcher:
    if name not in REGISTRY:
        raise KeyError(f"unknown fetcher: {name}")
    return REGISTRY[name](cfg)
