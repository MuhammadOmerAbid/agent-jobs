import os

import requests

from agent_jobs.fetchers.base import RawJobPosting, looks_remote, strip_html

SOURCE = "jooble"


def fetch() -> list[RawJobPosting]:
    api_key = os.environ.get("JOOBLE_API_KEY")
    if not api_key:
        return []

    response = requests.post(
        f"https://jooble.org/api/{api_key}",
        json={"keywords": "remote"},
        timeout=20,
    )
    response.raise_for_status()
    rows = response.json().get("jobs", [])

    postings = []
    for row in rows:
        title = row.get("title", "")
        snippet = row.get("snippet", "")
        if not looks_remote(title, snippet, row.get("location")):
            continue
        postings.append(
            RawJobPosting(
                source=SOURCE,
                source_native_id=str(row.get("id", row.get("link", ""))),
                title=title or "Untitled",
                company=row.get("company"),
                location=row.get("location") or "Remote",
                remote_type="fully_remote",
                jd_text=strip_html(snippet),
                apply_url=row.get("link", ""),
                posted_at=row.get("updated"),
                raw_json=row,
            )
        )
    return postings
