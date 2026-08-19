"""Configuration loader — reads settings.yaml + environment variables."""

from __future__ import annotations

import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

load_dotenv()

_ROOT = Path(__file__).parent.parent


def load_settings(path: Path | None = None) -> dict:
    cfg_path = path or _ROOT / "config" / "settings.yaml"
    with open(cfg_path) as f:
        return yaml.safe_load(f)


def get_anthropic_key() -> str:
    key = os.getenv("ANTHROPIC_API_KEY", "")
    if not key:
        raise EnvironmentError("ANTHROPIC_API_KEY is not set. Add it to your .env file.")
    return key


settings = load_settings()
