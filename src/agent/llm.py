"""
Thin LLM provider abstraction.

Supported providers:  anthropic | openai
Configured via settings.yaml:

  scoring:
    provider: anthropic        # or openai
    model: claude-sonnet-5     # or gpt-4o, gpt-4o-mini, etc.

Required env vars:
  ANTHROPIC_API_KEY   (when provider: anthropic)
  OPENAI_API_KEY      (when provider: openai)
"""

from __future__ import annotations

import os

from src.config import settings


def complete(system: str, user: str, max_tokens: int = 4096) -> str:
    """
    Send a system + user message to the configured LLM and return the text response.
    Drop-in for both Anthropic and OpenAI — callers don't need to know which.
    """
    cfg = settings.get("scoring", {})
    provider = cfg.get("provider", "anthropic").lower()
    model = cfg.get("model", "claude-sonnet-5")

    if provider == "openai":
        return _openai_complete(model, system, user, max_tokens)
    else:
        return _anthropic_complete(model, system, user, max_tokens)


# ---------------------------------------------------------------------------
# Anthropic
# ---------------------------------------------------------------------------

def _anthropic_complete(model: str, system: str, user: str, max_tokens: int) -> str:
    try:
        import anthropic  # noqa: PLC0415
    except ImportError as e:
        raise ImportError("anthropic package not installed: pip install anthropic") from e

    key = os.getenv("ANTHROPIC_API_KEY", "")
    if not key:
        raise EnvironmentError("ANTHROPIC_API_KEY is not set.")

    client = anthropic.Anthropic(api_key=key)
    message = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return message.content[0].text


# ---------------------------------------------------------------------------
# OpenAI
# ---------------------------------------------------------------------------

def _openai_complete(model: str, system: str, user: str, max_tokens: int) -> str:
    try:
        from openai import OpenAI  # noqa: PLC0415
    except ImportError as e:
        raise ImportError("openai package not installed: pip install openai") from e

    key = os.getenv("OPENAI_API_KEY", "")
    if not key:
        raise EnvironmentError("OPENAI_API_KEY is not set.")

    client = OpenAI(api_key=key)
    response = client.chat.completions.create(
        model=model,
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    return response.choices[0].message.content or ""
