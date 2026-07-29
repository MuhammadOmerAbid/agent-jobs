import requests

from agent_jobs.fetchers.base import RawJobPosting, strip_html

SOURCE = "remoteok"
URL = "https://remoteok.com/api"


def fetch() -> list[RawJobPosting]:
    response = requests.get(URL, headers={"User-Agent": "agent-jobs/1.0"}, timeout=20)
    response.raise_for_status()
    rows = response.json()

    postings = []
    for row in rows:
        if not isinstance(row, dict) or "id" not in row:
            continue  # first element is a legal-notice object, not a job
        postings.append(
            RawJobPosting(
                source=SOURCE,
                source_native_id=str(row["id"]),
                title=row.get("position", "Untitled"),
                company=row.get("company"),
                company_url=row.get("company_logo") and row.get("url"),
                location=row.get("location") or "Remote",
                remote_type="fully_remote",
                salary_min_usd=row.get("salary_min"),
                salary_max_usd=row.get("salary_max"),
                tags=row.get("tags") or [],
                jd_text=strip_html(row.get("description")),
                apply_url=row.get("url") or row.get("apply_url") or "",
                posted_at=row.get("date"),
                raw_json=row,
            )
        )
    return postings
