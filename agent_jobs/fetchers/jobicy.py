import requests

from agent_jobs.fetchers.base import RawJobPosting, strip_html

SOURCE = "jobicy"
URL = "https://jobicy.com/api/v2/remote-jobs"


def fetch() -> list[RawJobPosting]:
    response = requests.get(URL, headers={"User-Agent": "agent-jobs/1.0"}, timeout=20, params={"count": 50})
    response.raise_for_status()
    rows = response.json().get("jobs", [])

    postings = []
    for row in rows:
        # jobIndustry/jobType are arrays of strings in Jobicy's actual API
        # response (confirmed against a live call), not scalars.
        tags = [*_as_list(row.get("jobIndustry")), *_as_list(row.get("jobType"))]
        postings.append(
            RawJobPosting(
                source=SOURCE,
                source_native_id=str(row.get("id", "")),
                title=row.get("jobTitle", "Untitled"),
                company=row.get("companyName"),
                location=row.get("jobGeo") or "Remote",
                remote_type="fully_remote",
                salary_min_usd=row.get("annualSalaryMin"),
                salary_max_usd=row.get("annualSalaryMax"),
                tags=tags,
                jd_text=strip_html(row.get("jobDescription") or row.get("jobExcerpt")),
                apply_url=row.get("url", ""),
                posted_at=row.get("pubDate"),
                raw_json=row,
            )
        )
    return postings


def _as_list(value) -> list[str]:
    if not value:
        return []
    if isinstance(value, list):
        return [str(v) for v in value if v]
    return [str(value)]
