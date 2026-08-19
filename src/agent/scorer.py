"""Scores and summarizes Boston sports stories via the configured LLM provider."""

from __future__ import annotations

import json

from src.agent.llm import complete
from src.config import settings
from src.sources.rss import Story

_SYSTEM_PROMPT = """\
You are a die-hard Boston sports fan, beat reporter, and gossip hound.
You have deep knowledge of Boston sports history — not just the current rosters but
decades of lore, trades, controversies, personal dramas, and trivia involving BOTH
current and former players from the Celtics, Bruins, Red Sox, Patriots, and Revolution.

You evaluate news stories on these axes:
- **Newsworthiness** — trades, injuries, signings, firings, lineup changes
- **Gossip & drama** — personal life, feuds, beef, social media drama, controversies
- **Obscurity factor** — surprising historical facts, forgotten players resurfacing,
  weird trivia, "I didn't know that" moments about the franchise or a player
- **Former player interest** — stories about legends or former players that will
  delight long-time Boston fans (e.g. Bobby Orr spotted somewhere, Pedro Martinez's
  opinion on something, Tom Brady drama, Manny Ramirez update, etc.)
- **Fan mood impact** — news that will make fans cheer, groan, argue, or laugh

You respond with structured JSON only.\
"""

_SCORE_PROMPT = """\
Below are Boston sports stories pulled from news feeds, Reddit, and blogs.
For each story:
1. Score 0.0–1.0 on overall fan interest (NOT just newsworthiness — gossip,
   obscure facts, former player drama, and weird trivia can score just as high
   as a trade or injury if it's genuinely juicy or interesting)
2. Write a 1–2 sentence fan-friendly summary in a casual, excited voice
3. Assign a category tag

Score guidelines:
  0.9–1.0 → Must-read: shocking trade/signing, major scandal, juicy gossip,
             legendary player drama, historic milestone
  0.7–0.89 → Interesting: notable injury/return, funny moment, former player
              story, surprising stat, mid-level rumor
  0.5–0.69 → Worth a glance: practice notes, minor roster moves, mild drama
  < 0.5    → Skip: routine recaps, game summaries without storyline, filler

Categories: trade | injury | signing | gossip | former_player | rumor |
            history | drama | social_media | game | roster | other

Respond with a JSON array, one object per story, same order as input:
[
  {{
    "index": 0,
    "score": 0.87,
    "summary": "...",
    "category": "gossip"
  }},
  ...
]

Stories:
{stories}
"""


def score_stories(stories: list[Story]) -> list[dict]:
    """
    Score a batch of stories via the configured LLM provider.
    Returns list of dicts: story, score, summary, category.
    """
    if not stories:
        return []

    stories_text = "\n\n".join(
        f"[{i}] SOURCE: {s.source}\nTITLE: {s.title}\n{s.summary[:400]}"
        for i, s in enumerate(stories)
    )

    raw = complete(
        system=_SYSTEM_PROMPT,
        user=_SCORE_PROMPT.format(stories=stories_text),
        max_tokens=4096,
    ).strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    scored = json.loads(raw)

    return [
        {
            "story": stories[item["index"]],
            "score": item["score"],
            "summary": item["summary"],
            "category": item.get("category", "other"),
        }
        for item in scored
        if item["index"] < len(stories)
    ]


def score_in_batches(stories: list[Story], batch_size: int = 30) -> list[dict]:
    """Score stories in batches to stay within context limits."""
    all_scored: list[dict] = []
    for i in range(0, len(stories), batch_size):
        batch = stories[i : i + batch_size]
        all_scored.extend(score_stories(batch))
    return all_scored


def top_stories(
    stories: list[Story],
    n: int | None = None,
    min_score: float | None = None,
) -> list[dict]:
    """Score all stories and return the top-n above min_score, batching as needed."""
    cfg = settings.get("scoring", {})
    n = n or cfg.get("top_n", 5)
    min_score = min_score if min_score is not None else cfg.get("min_score", 0.6)

    scored = score_in_batches(stories)
    filtered = [s for s in scored if s["score"] >= min_score]
    filtered.sort(key=lambda x: x["score"], reverse=True)
    return filtered[:n]
