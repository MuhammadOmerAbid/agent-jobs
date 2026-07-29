import os

import requests

from agent_jobs.fetchers.base import RawJobPosting, looks_remote, strip_html
from agent_jobs.rate_limit.limiter import can_fetch, record_call

SOURCE = "adzuna"
COUNTRIES = ["us", "gb", "ca", "au", "de", "fr", "in", "nl", "es", "it",
             "pl", "br", "mx", "sg", "za", "nz", "at", "be", "ch"]


def fetch() -> list[RawJobPosting]:
    app_id = os.environ.get("ADZUNA_APP_ID")
    app_key = os.environ.get("ADZUNA_APP_KEY")
    if not app_id or not app_key:
        return []

    postings = []
    for country in COUNTRIES:
        if not can_fetch(SOURCE):
            break  # monthly budget exhausted, remaining countries wait for reset
        try:
            response = requests.get(
                f"https://api.adzuna.com/v1/api/jobs/{country}/search/1",
                params={
                    "app_id": app_id,
                    "app_key": app_key,
                    "results_per_page": 50,
                    "what": "remote",
                },
                timeout=20,
            )
            response.raise_for_status()
            record_call(SOURCE)
        except requests.RequestException:
            continue

        for row in response.json().get("results", []):
            description = row.get("description", "")
            title = row.get("title", "")
            if not looks_remote(title, description):
                continue
            postings.append(
                RawJobPosting(
                    source=SOURCE,
                    source_native_id=str(row.get("id", "")),
                    title=title or "Untitled",
                    company=(row.get("company") or {}).get("display_name"),
                    location=(row.get("location") or {}).get("display_name") or "Remote",
                    remote_type="fully_remote",
                    salary_min_usd=row.get("salary_min"),
                    salary_max_usd=row.get("salary_max"),
                    tags=[row.get("category", {}).get("label")] if row.get("category") else [],
                    jd_text=strip_html(description),
                    apply_url=row.get("redirect_url", ""),
                    posted_at=row.get("created"),
                    raw_json=row,
                )
            )
    return postings
