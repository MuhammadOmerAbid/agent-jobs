import requests

from agent_jobs.fetchers.base import RawJobPosting, strip_html

SOURCE = "arbeitnow"
URL = "https://www.arbeitnow.com/api/job-board-api"


def fetch() -> list[RawJobPosting]:
    response = requests.get(URL, headers={"User-Agent": "agent-jobs/1.0"}, timeout=20)
    response.raise_for_status()
    rows = response.json().get("data", [])

    postings = []
    for row in rows:
        if not row.get("remote"):
            continue
        postings.append(
            RawJobPosting(
                source=SOURCE,
                source_native_id=row.get("slug", ""),
                title=row.get("title", "Untitled"),
                company=row.get("company_name"),
                location=row.get("location") or "Remote",
                remote_type="fully_remote",
                tags=(row.get("tags") or []) + (row.get("job_types") or []),
                jd_text=strip_html(row.get("description")),
                apply_url=row.get("url", ""),
                posted_at=str(row.get("created_at", "")),
                raw_json=row,
            )
        )
    return postings
