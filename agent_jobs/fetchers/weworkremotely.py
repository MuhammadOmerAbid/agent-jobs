import feedparser

from agent_jobs.fetchers.base import RawJobPosting, strip_html

SOURCE = "weworkremotely"
FEED_URL = "https://weworkremotely.com/remote-jobs.rss"


def fetch() -> list[RawJobPosting]:
    feed = feedparser.parse(FEED_URL)

    postings = []
    for entry in feed.entries:
        title = entry.get("title", "Untitled")
        company = None
        role = title
        if ":" in title:
            company, role = title.split(":", 1)
            company, role = company.strip(), role.strip()

        postings.append(
            RawJobPosting(
                source=SOURCE,
                source_native_id=entry.get("id") or entry.get("link", ""),
                title=role,
                company=company,
                location="Remote",
                remote_type="fully_remote",
                tags=[t["term"] for t in entry.get("tags", [])] if entry.get("tags") else [],
                jd_text=strip_html(entry.get("summary")),
                apply_url=entry.get("link", ""),
                posted_at=entry.get("published"),
                raw_json={"title": title, "link": entry.get("link"), "published": entry.get("published")},
            )
        )
    return postings
