import os

import requests

from agent_jobs.fetchers.base import RawJobPosting, strip_html

SOURCE = "findwork"
URL = "https://findwork.dev/api/jobs/"


def fetch() -> list[RawJobPosting]:
    token = os.environ.get("FINDWORK_API_TOKEN")
    if not token:
        return []

    response = requests.get(
        URL,
        headers={"Authorization": f"Token {token}"},
        params={"remote": "true"},
        timeout=20,
    )
    response.raise_for_status()
    rows = response.json().get("results", [])

    postings = []
    for row in rows:
        postings.append(
            RawJobPosting(
                source=SOURCE,
                source_native_id=str(row.get("id", "")),
                title=row.get("role", "Untitled"),
                company=row.get("company_name"),
                location=row.get("location") or "Remote",
                remote_type="fully_remote" if row.get("remote") else "unclear",
                tags=row.get("keywords") or [],
                jd_text=strip_html(row.get("text")),
                apply_url=row.get("url", ""),
                posted_at=row.get("date_posted"),
                raw_json=row,
            )
        )
    return postings
