import re

import feedparser

from agent_jobs.fetchers.base import RawJobPosting, strip_html

SOURCE = "fourdayweek"
FEED_URL = "https://4dayweek.io/feed"

_TITLE_SUFFIX = re.compile(r"\s+at\s+.+$", re.IGNORECASE)


def fetch() -> list[RawJobPosting]:
    feed = feedparser.parse(FEED_URL)

    postings = []
    for entry in feed.entries:
        title = entry.get("title", "Untitled")
        company = entry.get("author") or None
        role = _TITLE_SUFFIX.sub("", title) if company else title

        postings.append(
            RawJobPosting(
                source=SOURCE,
                source_native_id=entry.get("id") or entry.get("link", ""),
                title=role,
                company=company,
                location="Remote / 4-day week",
                remote_type="unclear",
                tags=["4-day-week"],
                jd_text=strip_html(entry.get("summary")),
                apply_url=entry.get("link", ""),
                posted_at=entry.get("published"),
                raw_json={"title": title, "link": entry.get("link"), "author": entry.get("author")},
            )
        )
    return postings
