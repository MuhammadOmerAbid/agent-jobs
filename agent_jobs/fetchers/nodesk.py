import feedparser

from agent_jobs.fetchers.base import RawJobPosting, strip_html

SOURCE = "nodesk"
FEED_URL = "https://nodesk.substack.com/feed"


def fetch() -> list[RawJobPosting]:
    feed = feedparser.parse(FEED_URL)

    postings = []
    for entry in feed.entries:
        postings.append(
            RawJobPosting(
                source=SOURCE,
                source_native_id=entry.get("id") or entry.get("link", ""),
                title=entry.get("title", "Untitled"),
                location="Remote",
                remote_type="fully_remote",
                jd_text=strip_html(entry.get("summary")),
                apply_url=entry.get("link", ""),
                posted_at=entry.get("published"),
                raw_json={"title": entry.get("title"), "link": entry.get("link")},
            )
        )
    return postings
