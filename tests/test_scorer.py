"""Tests for the story scorer."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from src.sources.rss import Story
from src.agent.scorer import score_stories


def _make_story(title: str, summary: str = "") -> Story:
    return Story(title=title, url="https://example.com", summary=summary, published=None, source="test")


def test_score_stories_empty():
    assert score_stories([]) == []


@patch("src.agent.scorer.anthropic.Anthropic")
def test_score_stories_returns_scored(mock_anthropic_cls):
    """score_stories returns one result per story with score and summary."""
    mock_client = MagicMock()
    mock_anthropic_cls.return_value = mock_client
    mock_client.messages.create.return_value = MagicMock(
        content=[
            MagicMock(
                text='[{"index": 0, "score": 0.9, "summary": "Big trade news."}, '
                     '{"index": 1, "score": 0.4, "summary": "Routine update."}]'
            )
        ]
    )

    stories = [
        _make_story("Celtics trade star player"),
        _make_story("Bruins practice update"),
    ]

    results = score_stories(stories)
    assert len(results) == 2
    assert results[0]["score"] == 0.9
    assert results[1]["score"] == 0.4
    assert "Big trade" in results[0]["summary"]
