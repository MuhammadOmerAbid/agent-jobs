import requests

from agent_jobs.fetchers.base import RawJobPosting, strip_html

SOURCE = "workingnomads"
URL = "https://www.workingnomads.com/api/exposed_jobs/"


def fetch() -> list[RawJobPosting]:
    response = requests.get(URL, headers={"User-Agent": "agent-jobs/1.0"}, timeout=20)
    response.raise_for_status()
    rows = response.json()

    postings = []
    for row in rows:
        url = row.get("url", "")
        if not url:
            continue
        # tags is a comma-separated string in Working Nomads's actual API
        # response (confirmed against a live call), not an array.
        tag_string = row.get("tags") or ""
        tags = [t.strip() for t in tag_string.split(",") if t.strip()]
        if row.get("category_name"):
            tags.append(row["category_name"])

        postings.append(
            RawJobPosting(
                source=SOURCE,
                source_native_id=url,
                title=row.get("title", "Untitled"),
                company=row.get("company_name"),
                location=row.get("location") or "Remote",
                remote_type="fully_remote",
                tags=tags,
                jd_text=strip_html(row.get("description")),
                apply_url=url,
                posted_at=row.get("pub_date"),
                raw_json=row,
            )
        )
    return postings
