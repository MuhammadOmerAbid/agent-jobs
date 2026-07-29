import requests

from agent_jobs.fetchers.base import RawJobPosting, strip_html

SOURCE = "himalayas"
URL = "https://himalayas.app/jobs/api"


def fetch() -> list[RawJobPosting]:
    response = requests.get(URL, headers={"User-Agent": "agent-jobs/1.0"}, timeout=20)
    response.raise_for_status()
    payload = response.json()
    rows = payload.get("jobs", payload if isinstance(payload, list) else [])

    postings = []
    for row in rows:
        guid = str(row.get("guid") or row.get("id") or row.get("slug") or row.get("applicationLink", ""))
        if not guid:
            continue
        postings.append(
            RawJobPosting(
                source=SOURCE,
                source_native_id=guid,
                title=row.get("title", "Untitled"),
                company=(row.get("companyName") or (row.get("company") or {}).get("name")),
                location=row.get("locationRestrictions") and ", ".join(row.get("locationRestrictions")) or "Remote",
                remote_type="fully_remote",
                tags=row.get("categories") or row.get("tags") or [],
                jd_text=strip_html(row.get("description") or row.get("excerpt")),
                apply_url=row.get("applicationLink") or row.get("url") or "",
                posted_at=row.get("pubDate") or row.get("publishedAt"),
                raw_json=row,
            )
        )
    return postings
