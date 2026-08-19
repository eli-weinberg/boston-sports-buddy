"""
Boston Sports Buddy — main agent entrypoint.

Usage:
    python -m src.agent.buddy          # Run on schedule (daemon)
    python -m src.agent.buddy --once   # Run once and exit
"""

from __future__ import annotations

import argparse
import time

import schedule
from rich.console import Console

from src.agent.monitor import fetch_stories
from src.agent.scorer import top_stories
from src.config import settings

console = Console()


def _get_delivery():
    channel = settings.get("delivery", {}).get("channel", "console")
    if channel == "slack":
        from src.delivery.slack import deliver  # noqa: PLC0415
    elif channel == "email":
        from src.delivery.email import deliver  # noqa: PLC0415
    else:
        from src.delivery.console import deliver  # noqa: PLC0415
    return deliver


def run_once() -> None:
    """Fetch news, score it, and deliver highlights."""
    console.print("[dim]Fetching Boston sports news...[/dim]")
    stories = fetch_stories()
    console.print(f"[dim]Found {len(stories)} Boston-related stories. Scoring with Claude...[/dim]")

    top = top_stories(stories)

    deliver = _get_delivery()
    deliver(top)


def main() -> None:
    parser = argparse.ArgumentParser(description="Boston Sports Buddy")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    args = parser.parse_args()

    if args.once:
        run_once()
        return

    # Daemon mode
    interval = settings.get("schedule", {}).get("interval_minutes", 30)
    console.print(f"[green]Boston Sports Buddy started — checking every {interval} minutes.[/green]")
    console.print("[dim]Press Ctrl+C to stop.[/dim]\n")

    run_once()  # Run immediately on start
    schedule.every(interval).minutes.do(run_once)

    try:
        while True:
            schedule.run_pending()
            time.sleep(30)
    except KeyboardInterrupt:
        console.print("\n[dim]Stopped.[/dim]")


if __name__ == "__main__":
    main()
