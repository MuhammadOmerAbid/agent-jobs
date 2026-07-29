from datetime import datetime, timezone

from agent_jobs.config.profile import load_profile
from agent_jobs.db.repository import get_jobs, insert_score, upsert_job
from agent_jobs.fetchers import (
    adzuna, arbeitnow, findwork, fourdayweek, himalayas, hn_whoishiring, jobicy,
    jobspresso, jooble, nodesk, remoteok, remotive, themuse, weworkremotely,
    wellfound, workingnomads,
)
from agent_jobs.rate_limit.limiter import can_fetch, record_call, reset_at
from agent_jobs.scoring.scorer import score_job

FETCHERS = [
    (remoteok.SOURCE, remoteok.fetch),
    (weworkremotely.SOURCE, weworkremotely.fetch),
    (wellfound.SOURCE, wellfound.fetch),
    (arbeitnow.SOURCE, arbeitnow.fetch),
    (himalayas.SOURCE, himalayas.fetch),
    (jobicy.SOURCE, jobicy.fetch),
    (remotive.SOURCE, remotive.fetch),
    (nodesk.SOURCE, nodesk.fetch),
    (hn_whoishiring.SOURCE, hn_whoishiring.fetch),
    (themuse.SOURCE, themuse.fetch),
    (adzuna.SOURCE, adzuna.fetch),
    (findwork.SOURCE, findwork.fetch),
    (jooble.SOURCE, jooble.fetch),
    (workingnomads.SOURCE, workingnomads.fetch),
    (jobspresso.SOURCE, jobspresso.fetch),
    (fourdayweek.SOURCE, fourdayweek.fetch),
]


def run() -> None:
    profile = load_profile()
    total_new_or_updated = 0
    summary: dict[str, int] = {}

    for source, fetch_fn in FETCHERS:
        if not can_fetch(source):
            reset = reset_at(source)
            print(f"[run] {source}: rate-limit budget exhausted, skipping until {reset}")
            summary[source] = 0
            continue

        try:
            postings = fetch_fn()
            record_call(source)
        except Exception as error:
            print(f"[run] {source}: fetch failed ({error}), skipping")
            summary[source] = 0
            continue

        count = 0
        for posting in postings:
            job_id = upsert_job(posting.as_dict())
            job = {**posting.as_dict(), "id": job_id}
            try:
                result = score_job(job, profile)
                insert_score(
                    job_id, result["fit_score"], result["reasons"],
                    result["red_flags"], result["llm_powered"], profile,
                )
            except Exception as error:
                print(f"[run] scoring failed for job {job_id} ({error})")
            count += 1

        summary[source] = count
        total_new_or_updated += count
        print(f"[run] {source}: {count} postings processed")

    print(f"[run] done. {total_new_or_updated} postings processed across {len(FETCHERS)} sources "
          f"at {datetime.now(timezone.utc).isoformat()}")
    print(f"[run] per-source summary: {summary}")


def show_top(limit: int = 10) -> None:
    jobs = get_jobs({"limit": limit})
    for job in jobs:
        score = job.get("fit_score")
        print(f"[{score if score is not None else '?'}%] {job['title']} @ {job.get('company', '?')} "
              f"({job['source']}) -> {job['apply_url']}")
