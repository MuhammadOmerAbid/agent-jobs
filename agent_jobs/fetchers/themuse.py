import os

import requests

from agent_jobs.fetchers.base import RawJobPosting, looks_remote, strip_html

SOURCE = "themuse"
URL = "https://www.themuse.com/api/public/jobs"


def fetch() -> list[RawJobPosting]:
    params = {"page": 0}
    api_key = os.environ.get("THEMUSE_API_KEY")
    if api_key:
        params["api_key"] = api_key

    response = requests.get(URL, params=params, timeout=20)
    response.raise_for_status()
    rows = response.json().get("results", [])

    postings = []
    for row in rows:
        title = row.get("name", "")
        contents = row.get("contents", "")
        locations = ", ".join(loc.get("name", "") for loc in row.get("locations", []))
        if not looks_remote(title, contents, locations):
            continue
        postings.append(
            RawJobPosting(
                source=SOURCE,
                source_native_id=str(row.get("id", "")),
                title=title or "Untitled",
                company=(row.get("company") or {}).get("name"),
                location=locations or "Remote",
                remote_type="fully_remote",
                tags=[tag.get("name") for tag in row.get("tags", []) if tag.get("name")],
                jd_text=strip_html(contents),
                apply_url=(row.get("refs") or {}).get("landing_page", ""),
                posted_at=row.get("publication_date"),
                raw_json=row,
            )
        )
    return postings
