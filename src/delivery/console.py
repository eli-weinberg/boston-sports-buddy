"""Rich console delivery — prints highlights to the terminal."""

from __future__ import annotations

from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

console = Console()

TEAM_EMOJI = {
    "celtics": "🏀",
    "bruins": "🏒",
    "red sox": "⚾",
    "patriots": "🏈",
    "revolution": "⚽",
}


def _team_emoji(text: str) -> str:
    lower = text.lower()
    for team, emoji in TEAM_EMOJI.items():
        if team in lower:
            return emoji
    return "🗞️"


def deliver(top: list[dict]) -> None:
    """Print top stories to the terminal."""
    now = datetime.now().strftime("%a %b %-d, %Y  %-I:%M %p")

    console.print()
    console.print(
        Panel(
            f"[bold green]🏒 Boston Sports Buddy[/bold green]  ·  {now}",
            box=box.DOUBLE_EDGE,
            style="green",
        )
    )

    if not top:
        console.print("[dim]No interesting stories right now. Check back later![/dim]\n")
        return

    table = Table(box=box.SIMPLE_HEAD, show_header=True, header_style="bold cyan")
    table.add_column("", width=3)
    table.add_column("Score", width=7, justify="right")
    table.add_column("Headline", style="bold white", no_wrap=False)
    table.add_column("Digest", style="dim", no_wrap=False)

    for item in top:
        story = item["story"]
        score = item["score"]
        summary = item["summary"]
        emoji = _team_emoji(story.title + " " + story.summary)
        score_str = f"[green]{score:.2f}[/green]" if score >= 0.8 else f"[yellow]{score:.2f}[/yellow]"
        table.add_row(emoji, score_str, story.title, summary)

    console.print(table)
    console.print()

    # Print URLs
    for i, item in enumerate(top, 1):
        console.print(f"  [dim]{i}.[/dim] {item['story'].url}")
    console.print()
