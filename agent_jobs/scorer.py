import json
from shared.llm import ask
from agent_jobs.db import get_unscored_jobs, save_score

_SYSTEM = """You are a job-fit evaluator. Given a job posting and a candidate profile,
return a JSON object with keys: fit_pct (int 0-100), pros (list of strings), red_flags (list of strings).
Return only valid JSON, no explanation."""


def score_job(job: dict, profile: dict) -> tuple[int, str, str]:
    prompt = f"Profile:\n{json.dumps(profile, indent=2)}\n\nJob:\nTitle: {job['title']}\nCompany: {job['company']}\nDescription: {job['description'][:1000]}"
    raw = ask(system=_SYSTEM, user=prompt, max_tokens=256)
    try:
        data = json.loads(raw)
        fit_pct = int(data.get("fit_pct", 0))
        pros = "; ".join(data.get("pros", []))
        red_flags = "; ".join(data.get("red_flags", []))
    except Exception:
        fit_pct, pros, red_flags = 0, "", "parse error"
    return fit_pct, pros, red_flags


def score_all(profile: dict) -> int:
    jobs = get_unscored_jobs()
    for job in jobs:
        fit_pct, pros, red_flags = score_job(job, profile)
        save_score(job["id"], fit_pct, pros, red_flags)
    return len(jobs)
