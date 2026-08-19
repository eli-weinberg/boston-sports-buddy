"""News monitoring loop — fetches from all configured sources."""

from __future__ import annotations

from src.config import settings
from src.sources.rss import Story, fetch_all as fetch_rss


def fetch_stories() -> list[Story]:
    """Pull stories from all enabled sources and deduplicate by URL."""
    all_stories: list[Story] = []
    seen_urls: set[str] = set()

    def add(stories: list[Story]) -> None:
        for s in stories:
            if s.url not in seen_urls:
                seen_urls.add(s.url)
                all_stories.append(s)

    source_cfg = settings.get("sources", {})

    # ── RSS ──────────────────────────────────────────────────────────────
    rss_cfg = source_cfg.get("rss", {})
    if rss_cfg.get("enabled", True):
        custom_feeds = rss_cfg.get("feeds")  # None → use DEFAULT_FEEDS
        add(fetch_rss(custom_feeds))

    # ── Reddit ────────────────────────────────────────────────────────────
    reddit_cfg = source_cfg.get("reddit", {})
    if reddit_cfg.get("enabled", False):
        try:
            from src.sources.reddit import fetch_subreddits  # noqa: PLC0415

            subreddits = reddit_cfg.get("subreddits") or None  # None → use defaults
            sort = reddit_cfg.get("sort", "hot")
            add(fetch_subreddits(subreddits, sort=sort))
        except ImportError:
            print("[monitor] Reddit source requires praw: pip install praw")
        except KeyError as exc:
            print(f"[monitor] Reddit credentials missing: {exc}. Set REDDIT_CLIENT_ID/SECRET in .env")

    # ── Web scraping ──────────────────────────────────────────────────────
    web_cfg = source_cfg.get("web", {})
    if web_cfg.get("enabled", True):
        try:
            from src.sources.web import fetch_all_web  # noqa: PLC0415

            add(fetch_all_web())
        except ImportError:
            print("[monitor] Web scraping requires httpx: pip install httpx")

    print(f"[monitor] {len(all_stories)} unique stories fetched from all sources")
    return all_stories
