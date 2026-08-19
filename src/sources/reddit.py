"""Reddit source — pulls top/hot posts from Boston sports subreddits via PRAW."""

from __future__ import annotations

import os
from datetime import datetime, timezone

import praw

from src.sources.rss import Story


def _get_reddit() -> praw.Reddit:
    return praw.Reddit(
        client_id=os.environ["REDDIT_CLIENT_ID"],
        client_secret=os.environ["REDDIT_CLIENT_SECRET"],
        user_agent=os.getenv("REDDIT_USER_AGENT", "boston-sports-buddy/0.1"),
        # read-only — no username/password needed
    )


# Subreddits to monitor and how many posts to pull per run
SUBREDDIT_CONFIG: dict[str, int] = {
    # Team-specific
    "bostonceltics": 25,
    "BostonBruins": 25,
    "redsox": 25,
    "Patriots": 25,
    # Broader leagues — we'll filter for Boston relevance downstream via scorer
    "nba": 15,
    "hockey": 15,
    "baseball": 15,
    "nfl": 15,
    # Meta / gossip
    "sportsgossip": 20,
    "nbagoat": 10,      # debates often surface Boston legends
    "PatriotsDynasty": 15,
}


def _post_to_story(post: praw.models.Submission, source_label: str) -> Story:
    body = post.selftext[:500] if post.selftext else ""
    published = datetime.fromtimestamp(post.created_utc, tz=timezone.utc).replace(tzinfo=None)
    return Story(
        title=post.title,
        url=f"https://reddit.com{post.permalink}",
        summary=body or f"[{post.score} upvotes · {post.num_comments} comments]",
        published=published,
        source=f"r/{source_label}",
        tags=["reddit"],
    )


def fetch_subreddits(
    subreddits: list[str] | None = None,
    limit_per_sub: int | None = None,
    sort: str = "hot",
) -> list[Story]:
    """
    Pull posts from subreddits.
    `sort` can be 'hot', 'new', or 'top' (day).
    Falls back to SUBREDDIT_CONFIG if `subreddits` not given.
    """
    reddit = _get_reddit()
    seen_urls: set[str] = set()
    stories: list[Story] = []

    sub_map = {s: limit_per_sub or SUBREDDIT_CONFIG.get(s, 20) for s in (subreddits or SUBREDDIT_CONFIG)}

    for sub_name, limit in sub_map.items():
        try:
            subreddit = reddit.subreddit(sub_name)
            if sort == "new":
                posts = subreddit.new(limit=limit)
            elif sort == "top":
                posts = subreddit.top("day", limit=limit)
            else:
                posts = subreddit.hot(limit=limit)

            for post in posts:
                if post.stickied:
                    continue
                url = f"https://reddit.com{post.permalink}"
                if url in seen_urls:
                    continue
                seen_urls.add(url)
                stories.append(_post_to_story(post, sub_name))
        except Exception as exc:  # noqa: BLE001
            print(f"[reddit] Failed to fetch r/{sub_name}: {exc}")

    return stories
