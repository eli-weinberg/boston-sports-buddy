"""Rich console delivery — prints highlights to the terminal."""

from __future__ import annotations

from datetime import datetime

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

TEAM_EMOJI = {
    "celtics": "🏀",
    "bruins": "🏒",
    "red sox": "⚾",
    "redsox": "⚾",
    "patriots": "🏈",
    "revolution": "⚽",
}

CATEGORY_EMOJI = {
    "trade": "🔄",
    "injury": "🩹",
    "signing": "✍️",
    "gossip": "👀",
    "former_player": "🏆",
    "rumor": "🗣️",
    "history": "📜",
    "drama": "🔥",
    "social_media": "📱",
    "game": "🎮",
    "roster": "📋",
    "other": "🗞️",
}


def _team_emoji(text: str) -> str:
    lower = text.lower()
    for team, emoji in TEAM_EMOJI.items():
        if team in lower:
            return emoji
    return "🗞️"


def _score_color(score: float) -> str:
    if score >= 0.85:
        return "bold red"
    if score >= 0.70:
        return "yellow"
    return "green"


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
        console.print("[dim]No stories cleared the threshold. Check back later![/dim]\n")
        return

    table = Table(box=box.SIMPLE_HEAD, show_header=True, header_style="bold cyan", padding=(0, 1))
    table.add_column("", width=2, no_wrap=True)      # team emoji
    table.add_column("", width=2, no_wrap=True)      # category emoji
    table.add_column("Score", width=6, justify="right")
    table.add_column("Headline", style="bold white", ratio=2, no_wrap=False)
    table.add_column("Buddy's Take", style="dim", ratio=3, no_wrap=False)

    for item in top:
        story = item["story"]
        score = item["score"]
        cat = item.get("category", "other")
        color = _score_color(score)
        table.add_row(
            _team_emoji(story.title + " " + story.summary),
            CATEGORY_EMOJI.get(cat, "🗞️"),
            f"[{color}]{score:.2f}[/{color}]",
            story.title,
            item["summary"],
        )

    console.print(table)
    console.print()

    for i, item in enumerate(top, 1):
        src = item["story"].source
        console.print(f"  [dim]{i}. [{src}][/dim] {item['story'].url}")
    console.print()
