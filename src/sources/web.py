"""
Lightweight web scraper for Boston sports sites that lack usable RSS feeds.
Uses httpx + basic HTML parsing (no heavy dependencies like BeautifulSoup).
Headlines + links only — full text is intentionally skipped.
"""

from __future__ import annotations

import re
from datetime import datetime

import httpx

from src.sources.rss import Story

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    )
}

# Each entry: (display_name, url, headline_pattern)
# The pattern must have one capture group that extracts the headline text.
SCRAPED_SITES: list[tuple[str, str, str]] = [
    (
        "WEEI",
        "https://www.weei.com/sports/boston",
        r'<h[23][^>]*>\s*<a[^>]+href="(/[^"]+)"[^>]*>\s*([^<]{20,200})\s*</a>',
    ),
    (
        "NBC Sports Boston",
        "https://www.nbcsportsboston.com/",
        r'<h[23][^>]*class="[^"]*title[^"]*"[^>]*>\s*<a[^>]+href="(https://www\.nbcsportsboston\.com/[^"]+)"[^>]*>\s*([^<]{20,200})\s*</a>',
    ),
]

_BASE_URLS = {
    "WEEI": "https://www.weei.com",
}


def _scrape_site(name: str, url: str, pattern: str) -> list[Story]:
    try:
        resp = httpx.get(url, headers=_HEADERS, timeout=10, follow_redirects=True)
        resp.raise_for_status()
    except Exception as exc:  # noqa: BLE001
        print(f"[web] Failed to fetch {name}: {exc}")
        return []

    html = resp.text
    stories: list[Story] = []
    seen: set[str] = set()

    for m in re.finditer(pattern, html, re.DOTALL):
        href, headline = m.group(1).strip(), m.group(2).strip()
        headline = re.sub(r"\s+", " ", headline)
        if not href or not headline or href in seen:
            continue
        seen.add(href)

        base = _BASE_URLS.get(name, "")
        full_url = href if href.startswith("http") else base + href

        stories.append(
            Story(
                title=headline,
                url=full_url,
                summary="",
                published=datetime.now(),
                source=name,
                tags=["web"],
            )
        )

    return stories


def fetch_all_web() -> list[Story]:
    stories: list[Story] = []
    for name, url, pattern in SCRAPED_SITES:
        stories.extend(_scrape_site(name, url, pattern))
    return stories
