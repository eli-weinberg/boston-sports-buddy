"""Generic RSS feed reader. Returns a list of story dicts."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

import feedparser


@dataclass
class Story:
    title: str
    url: str
    summary: str
    published: datetime | None
    source: str
    tags: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Keywords — current teams + venues
# ---------------------------------------------------------------------------
BOSTON_TEAM_KEYWORDS = {
    "celtics", "bruins", "red sox", "redsox", "patriots", "revolution",
    "boston", "fenway", "td garden", "gillette stadium", "foxborough",
    "new england patriots", "new england revolution",
}

# ---------------------------------------------------------------------------
# Former player names — cast a wide net for gossip & legacy stories
# ---------------------------------------------------------------------------
FORMER_PLAYER_KEYWORDS = {
    # Celtics legends & recent
    "larry bird", "bill russell", "bob cousy", "john havlicek", "dave cowens",
    "kevin mchale", "robert parish", "dennis johnson", "jo jo white",
    "paul pierce", "kevin garnett", "ray allen", "antoine walker",
    "reggie lewis", "len bias", "isaiah thomas", "avery bradley",
    "jae crowder", "marcus smart", "jaylen brown",  # recent departed
    # Bruins legends & recent
    "bobby orr", "ray bourque", "cam neely", "phil esposito", "terry o'reilly",
    "milt schmidt", "gerry cheevers", "brad park", "johnny bucyk",
    "zdeno chara", "patrice bergeron", "david krejci", "milan lucic",
    "marc savard", "joe thornton", "tyler seguin", "dennis seidenberg",
    # Red Sox legends & recent
    "ted williams", "carl yastrzemski", "carlton fisk", "jim rice",
    "dwight evans", "pedro martinez", "curt schilling", "roger clemens",
    "wade boggs", "johnny pesky", "dom dimaggio", "rico petrocelli",
    "david ortiz", "big papi", "manny ramirez", "nomar garciaparra",
    "kevin youkilis", "dustin pedroia", "jonny gomes", "jason varitek",
    "jon lester", "clay buchholz", "john farrell", "trot nixon",
    "johnny damon", "derek lowe", "tim wakefield",
    # Patriots legends & recent
    "tom brady", "bill belichick", "randy moss", "tedy bruschi",
    "wes welker", "troy brown", "deion branch", "corey dillon",
    "mike vrabel", "richard seymour", "willie mcginest", "ty law",
    "adam vinatieri", "julian edelman", "rob gronkowski", "gronk",
    "james white", "danny amendola", "dion lewis", "malcolm butler",
    "dont'a hightower", "nate solder", "logan mankins", "vince wilfork",
    "brandin cooks", "antonio brown",
}

ALL_KEYWORDS = BOSTON_TEAM_KEYWORDS | FORMER_PLAYER_KEYWORDS


# ---------------------------------------------------------------------------
# RSS feed catalog
# ---------------------------------------------------------------------------
DEFAULT_FEEDS: list[tuple[str, str]] = [
    # ── ESPN ──────────────────────────────────────────────────────────────
    ("ESPN NBA",        "https://www.espn.com/espn/rss/nba/news"),
    ("ESPN NHL",        "https://www.espn.com/espn/rss/nhl/news"),
    ("ESPN MLB",        "https://www.espn.com/espn/rss/mlb/news"),
    ("ESPN NFL",        "https://www.espn.com/espn/rss/nfl/news"),
    # ── NBC Sports ────────────────────────────────────────────────────────
    ("NBC Sports",      "https://www.nbcsports.com/feed"),
    # ── Boston Globe ──────────────────────────────────────────────────────
    ("Boston Globe Sports", "https://www.bostonglobe.com/arc/outboundfeeds/rss/sports/"),
    # ── Boston Herald ─────────────────────────────────────────────────────
    ("Boston Herald Sports", "https://www.bostonherald.com/feed/?post_type=post&category_name=sports"),
    # ── MassLive ──────────────────────────────────────────────────────────
    ("MassLive Celtics",  "https://www.masslive.com/celtics/rss.xml"),
    ("MassLive Patriots", "https://www.masslive.com/patriots/rss.xml"),
    ("MassLive Red Sox",  "https://www.masslive.com/redsox/rss.xml"),
    ("MassLive Bruins",   "https://www.masslive.com/bruins/rss.xml"),
    # ── The Athletic (public feed) ────────────────────────────────────────
    ("The Athletic Boston", "https://theathletic.com/boston/feed/"),
    # ── SB Nation team blogs ──────────────────────────────────────────────
    ("CelticsBlog",         "https://www.celticsblog.com/rss/current"),
    ("Over the Monster",    "https://www.overthemonster.com/rss/current"),
    ("Stanley Cup of Chowder", "https://www.stanleycupofchowder.com/rss/current"),
    ("Pats Pulpit",         "https://www.patspulpit.com/rss/current"),
    ("The Bent Musket",     "https://www.thebentmusket.com/rss/current"),
    # ── Pro Football Talk (Patriots heavy) ────────────────────────────────
    ("ProFootballTalk",     "https://profootballtalk.nbcsports.com/feed/"),
    # ── Barstool Sports (gossip-heavy) ────────────────────────────────────
    ("Barstool Sports",     "https://www.barstoolsports.com/rss"),
    # ── Bleacher Report ───────────────────────────────────────────────────
    ("Bleacher Report NBA", "https://bleacherreport.com/nba.rss"),
    ("Bleacher Report NHL", "https://bleacherreport.com/nhl.rss"),
    ("Bleacher Report MLB", "https://bleacherreport.com/mlb.rss"),
    ("Bleacher Report NFL", "https://bleacherreport.com/nfl.rss"),
    # ── Yahoo Sports ──────────────────────────────────────────────────────
    ("Yahoo Sports NBA",    "https://sports.yahoo.com/nba/rss.xml"),
    ("Yahoo Sports NFL",    "https://sports.yahoo.com/nfl/rss.xml"),
    ("Yahoo Sports MLB",    "https://sports.yahoo.com/mlb/rss.xml"),
    ("Yahoo Sports NHL",    "https://sports.yahoo.com/nhl/rss.xml"),
    # ── Gossip / celebrity crossover ──────────────────────────────────────
    ("TMZ Sports",          "https://www.tmz.com/sports/rss.xml"),
    ("Page Six Sports",     "https://pagesix.com/sports/feed/"),
]


def _is_relevant(text: str) -> bool:
    lower = text.lower()
    return any(kw in lower for kw in ALL_KEYWORDS)


def fetch_feed(url: str, source_name: str = "") -> list[Story]:
    """Fetch a single RSS feed and return relevant stories."""
    feed = feedparser.parse(url)
    display = source_name or feed.feed.get("title", url)
    stories: list[Story] = []

    for entry in feed.entries:
        title = entry.get("title", "")
        summary = entry.get("summary", "")

        if not _is_relevant(title + " " + summary):
            continue

        published = None
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            try:
                published = datetime(*entry.published_parsed[:6])
            except Exception:  # noqa: BLE001
                pass

        stories.append(
            Story(
                title=title,
                url=entry.get("link", ""),
                summary=summary,
                published=published,
                source=display,
            )
        )

    return stories


def fetch_all(feeds: list[str] | list[tuple[str, str]] | None = None) -> list[Story]:
    """
    Fetch multiple RSS feeds and deduplicate by URL.
    Accepts either a list of URL strings or (name, url) tuples.
    Defaults to DEFAULT_FEEDS if not provided.
    """
    if feeds is None:
        feed_list: list[tuple[str, str]] = DEFAULT_FEEDS
    elif feeds and isinstance(feeds[0], str):
        feed_list = [("", url) for url in feeds]  # type: ignore[index]
    else:
        feed_list = feeds  # type: ignore[assignment]

    seen: set[str] = set()
    all_stories: list[Story] = []

    for name, url in feed_list:
        try:
            for story in fetch_feed(url, name):
                if story.url and story.url not in seen:
                    seen.add(story.url)
                    all_stories.append(story)
        except Exception as exc:  # noqa: BLE001
            print(f"[rss] Failed to fetch {name or url}: {exc}")

    return all_stories
