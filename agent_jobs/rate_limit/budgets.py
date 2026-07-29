"""Per-source free-tier budgets: (call_budget, window_seconds).

These are conservative defaults derived from each source's published free-tier
docs (see agent-jobs/README.md's per-source notes). Treat as starting points —
the limiter also backs off on observed errors/429s, not just this static table.

Sources with no published hard cap (RemoteOK, WeWorkRemotely, Wellfound,
Arbeitnow, Himalayas, Jobicy, Hacker News, NoDesk) still get an entry so every
fetch is recorded for observability, using a generous daily budget that is
never expected to bind in normal (once- or few-times-daily) usage.
"""

DAY = 86400
HOUR = 3600
MONTH = 30 * DAY

BUDGETS: dict[str, tuple[int, int]] = {
    "remoteok": (200, DAY),
    "weworkremotely": (200, DAY),
    "wellfound": (200, DAY),
    "arbeitnow": (200, DAY),
    "himalayas": (200, DAY),
    "jobicy": (200, DAY),
    "hn_whoishiring": (50, DAY),
    "nodesk": (200, DAY),
    "remotive": (4, DAY),
    "adzuna": (1000, MONTH),
    "findwork": (3600, HOUR),
    "jooble": (500, DAY),
    "themuse": (500, HOUR),
    "workingnomads": (200, DAY),
    "jobspresso": (200, DAY),
    "fourdayweek": (200, DAY),
}


def budget_for(source: str) -> tuple[int, int]:
    return BUDGETS.get(source, (100, DAY))
