# 🏒 Boston Sports Buddy

An agentic AI system that monitors Boston sports news, surfaces the most interesting stories, and delivers curated highlights — powered by the Claude API.

## Teams Covered

- 🏀 **Celtics** (NBA)
- 🏒 **Bruins** (NHL)
- ⚾ **Red Sox** (MLB)
- 🏈 **Patriots** (NFL)
- ⚽ **Revolution** (MLS)

## What It Does

1. **Monitors** — Polls sports news feeds (ESPN, RSS, Reddit, team sites) on a configurable schedule
2. **Analyzes** — Claude evaluates each story for newsworthiness, surprise factor, and fan relevance
3. **Highlights** — Surfaces top stories with a short AI-generated digest
4. **Delivers** — Sends highlights via your preferred channel (Slack, email, terminal)

## Project Structure

```
boston-sports-buddy/
├── src/
│   ├── agent/
│   │   ├── buddy.py          # Main agent entrypoint
│   │   ├── monitor.py        # News monitoring loop
│   │   └── scorer.py         # Story relevance scoring via Claude
│   ├── sources/
│   │   ├── espn.py           # ESPN news feed
│   │   ├── reddit.py         # r/bostonceltics, r/hockey, etc.
│   │   └── rss.py            # Generic RSS feed reader
│   ├── delivery/
│   │   ├── slack.py          # Slack webhook delivery
│   │   ├── email.py          # Email delivery
│   │   └── console.py        # Console/terminal output
│   └── config.py             # Configuration loader
├── config/
│   └── settings.yaml         # Teams, sources, delivery, schedule
├── tests/
│   └── test_scorer.py
├── pyproject.toml
├── .env.example
└── README.md
```

## Quick Start

```bash
# Install dependencies
pip install -e ".[dev]"

# Copy and fill in your config
cp .env.example .env

# Run once (print highlights to console)
python -m src.agent.buddy --once

# Run on a schedule (default: every 30 min)
python -m src.agent.buddy
```

## Configuration

Edit `config/settings.yaml` to tune teams, sources, and delivery:

```yaml
teams:
  - celtics
  - bruins
  - red_sox
  - patriots

schedule:
  interval_minutes: 30

delivery:
  channel: console   # console | slack | email
```

Set secrets in `.env`:

```
ANTHROPIC_API_KEY=sk-ant-...
SLACK_WEBHOOK_URL=https://hooks.slack.com/...
```

## Development

```bash
# Run tests
pytest

# Lint
ruff check src/
```

## License

MIT
