"""Uses Claude to score and summarize Boston sports stories."""

from __future__ import annotations

import json

import anthropic

from src.config import get_anthropic_key, settings
from src.sources.rss import Story

_SYSTEM_PROMPT = """\
You are a passionate Boston sports fan and sharp sports journalist. \
You evaluate news stories about Boston sports teams for how interesting, \
surprising, or important they are to a typical Boston fan. \
You respond with structured JSON only.\
"""

_SCORE_PROMPT = """\
Below are Boston sports news stories. For each one:
1. Score its newsworthiness from 0.0 (routine/boring) to 1.0 (must-read/shocking)
2. Write a 1-2 sentence fan-friendly summary

Respond with a JSON array, one object per story, in the same order:
[
  {{
    "index": 0,
    "score": 0.85,
    "summary": "..."
  }},
  ...
]

Stories:
{stories}
"""


def score_stories(stories: list[Story]) -> list[dict]:
    """
    Score a batch of stories with Claude.
    Returns list of dicts with keys: story, score, summary.
    """
    if not stories:
        return []

    client = anthropic.Anthropic(api_key=get_anthropic_key())
    model = settings.get("scoring", {}).get("model", "claude-sonnet-5")

    # Format stories for the prompt
    stories_text = "\n\n".join(
        f"[{i}] {s.title}\n{s.summary[:300]}" for i, s in enumerate(stories)
    )

    message = client.messages.create(
        model=model,
        max_tokens=2048,
        system=_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": _SCORE_PROMPT.format(stories=stories_text),
            }
        ],
    )

    raw = message.content[0].text.strip()
    # Strip markdown code fences if present
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
        }
        for item in scored
        if item["index"] < len(stories)
    ]


def top_stories(stories: list[Story], n: int | None = None, min_score: float | None = None) -> list[dict]:
    """Score all stories and return the top-n above min_score."""
    cfg = settings.get("scoring", {})
    n = n or cfg.get("top_n", 5)
    min_score = min_score if min_score is not None else cfg.get("min_score", 0.6)

    scored = score_stories(stories)
    filtered = [s for s in scored if s["score"] >= min_score]
    filtered.sort(key=lambda x: x["score"], reverse=True)
    return filtered[:n]
