import feedparser

from agent_jobs.fetchers.base import RawJobPosting, strip_html

SOURCE = "jobspresso"
FEED_URL = "https://jobspresso.co/feed/?post_type=job_listing"


def _split_author(author: str) -> tuple[str, str]:
    # Jobspresso's <author> is "Company Name<br>[glyph] Location" — confirmed
    # against a live feed sample, not documented anywhere.
    if not author:
        return "", ""
    parts = author.split("<br>", 1)
    company = strip_html(parts[0]).strip()
    location = strip_html(parts[1]).strip(" ⚲ ") if len(parts) > 1 else ""
    return company, location


def fetch() -> list[RawJobPosting]:
    feed = feedparser.parse(FEED_URL)

    postings = []
    for entry in feed.entries:
        company, location = _split_author(entry.get("author", ""))
        postings.append(
            RawJobPosting(
                source=SOURCE,
                source_native_id=entry.get("id") or entry.get("link", ""),
                title=entry.get("title", "Untitled"),
                company=company or None,
                location=location or "Remote",
                remote_type="fully_remote",
                tags=[t["term"] for t in entry.get("tags", [])] if entry.get("tags") else [],
                jd_text=strip_html(entry.get("summary")),
                apply_url=entry.get("link", ""),
                posted_at=entry.get("published"),
                raw_json={"title": entry.get("title"), "link": entry.get("link"), "author": entry.get("author")},
            )
        )
    return postings
