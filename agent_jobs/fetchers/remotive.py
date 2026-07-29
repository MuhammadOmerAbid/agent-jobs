import requests

from agent_jobs.fetchers.base import RawJobPosting, strip_html

SOURCE = "remotive"
URL = "https://remotive.com/api/remote-jobs"


def fetch() -> list[RawJobPosting]:
    response = requests.get(URL, headers={"User-Agent": "agent-jobs/1.0"}, timeout=20)
    response.raise_for_status()
    rows = response.json().get("jobs", [])

    postings = []
    for row in rows:
        postings.append(
            RawJobPosting(
                source=SOURCE,
                source_native_id=str(row.get("id", "")),
                title=row.get("title", "Untitled"),
                company=row.get("company_name"),
                location=row.get("candidate_required_location") or "Remote",
                remote_type="fully_remote",
                tags=row.get("tags") or [],
                jd_text=strip_html(row.get("description")),
                apply_url=row.get("url", ""),
                posted_at=row.get("publication_date"),
                raw_json=row,
            )
        )
    return postings
