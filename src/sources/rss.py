"""Generic RSS feed reader. Returns a list of story dicts."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

import feedparser


@dataclass
class Story:
    title: str
    url: str
    summary: str
    published: datetime | None
    source: str
    tags: list[str] = field(default_factory=list)


BOSTON_KEYWORDS = {
    "celtics", "bruins", "red sox", "patriots", "revolution",
    "boston", "fenway", "td garden", "foxborough", "gillette",
}


def _is_boston_related(text: str) -> bool:
    lower = text.lower()
    return any(kw in lower for kw in BOSTON_KEYWORDS)


def fetch_feed(url: str) -> list[Story]:
    """Fetch an RSS feed and return Boston-relevant stories."""
    feed = feedparser.parse(url)
    stories: list[Story] = []

    for entry in feed.entries:
        title = entry.get("title", "")
        summary = entry.get("summary", "")

        if not _is_boston_related(title + " " + summary):
            continue

        published = None
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            published = datetime(*entry.published_parsed[:6])

        stories.append(
            Story(
                title=title,
                url=entry.get("link", ""),
                summary=summary,
                published=published,
                source=feed.feed.get("title", url),
            )
        )

    return stories


def fetch_all(feeds: list[str]) -> list[Story]:
    """Fetch multiple RSS feeds and deduplicate by URL."""
    seen: set[str] = set()
    all_stories: list[Story] = []
    for feed_url in feeds:
        for story in fetch_feed(feed_url):
            if story.url not in seen:
                seen.add(story.url)
                all_stories.append(story)
    return all_stories
