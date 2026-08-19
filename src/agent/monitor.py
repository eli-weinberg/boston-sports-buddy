"""News monitoring loop — fetches from all configured sources."""

from __future__ import annotations

from src.config import settings
from src.sources.rss import Story, fetch_all


def fetch_stories() -> list[Story]:
    """Pull stories from all enabled sources."""
    all_stories: list[Story] = []

    source_cfg = settings.get("sources", {})

    # RSS feeds
    rss_cfg = source_cfg.get("rss", {})
    if rss_cfg.get("enabled", True):
        feeds = rss_cfg.get("feeds", [])
        all_stories.extend(fetch_all(feeds))

    # Reddit (optional)
    reddit_cfg = source_cfg.get("reddit", {})
    if reddit_cfg.get("enabled", False):
        try:
            from src.sources.reddit import fetch_subreddits  # noqa: PLC0415

            subreddits = reddit_cfg.get("subreddits", [])
            all_stories.extend(fetch_subreddits(subreddits))
        except ImportError:
            print("Reddit source requires praw. Install with: pip install praw")

    return all_stories
