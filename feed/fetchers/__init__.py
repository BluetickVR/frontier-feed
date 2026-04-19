from feed.fetchers.base import BaseFetcher
from feed.fetchers.github_trending import GitHubTrendingFetcher
from feed.fetchers.watchlist_twitter import WatchlistTwitterFetcher
from feed.fetchers.hf_papers import HFPapersFetcher
from feed.fetchers.show_hn import ShowHNFetcher
from feed.fetchers.github_releases import GitHubReleasesFetcher

REGISTRY: dict[str, type[BaseFetcher]] = {
    "github_trending": GitHubTrendingFetcher,
    "watchlist_twitter": WatchlistTwitterFetcher,
    "hf_papers": HFPapersFetcher,
    "show_hn": ShowHNFetcher,
    "tool_changelogs": GitHubReleasesFetcher,
}


def build_fetcher(name: str, cfg: dict) -> BaseFetcher:
    if name not in REGISTRY:
        raise KeyError(f"unknown fetcher: {name}")
    return REGISTRY[name](cfg)
