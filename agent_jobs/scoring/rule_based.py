"""Rule-based fit scorer, used when no LLM keys are configured or the LLM
call fails. Mirrors the "works without any API key" philosophy already
established in agent-ats's bk/app/services/optimizer.py.
"""


def score_job_rule_based(job: dict, profile: dict) -> dict:
    text = f"{job.get('title', '')} {job.get('jd_text', '')}".lower()
    tags = [str(t).lower() for t in (job.get("tags") or []) if t]

    tech_stack = [t.lower() for t in profile.get("tech_stack", [])]
    roles = [r.lower() for r in profile.get("roles", [])]
    no_go = [n.lower() for n in profile.get("no_go", [])]

    reasons = []
    red_flags = []

    stack_hits = [t for t in tech_stack if t in text or t in tags]
    role_hits = [r for r in roles if r in text]

    stack_score = (len(stack_hits) / len(tech_stack) * 60) if tech_stack else 30
    role_score = 30 if role_hits else 0

    salary_score = 10
    salary_min = job.get("salary_min_usd")
    profile_min = profile.get("salary_min_usd")
    if salary_min and profile_min and salary_min < profile_min:
        salary_score = 0
        red_flags.append(f"Posted salary (${salary_min}) is below your minimum (${profile_min})")

    for term in no_go:
        if term and term in text:
            red_flags.append(f"Mentions a no-go term: '{term}'")

    if stack_hits:
        reasons.append(f"Matches your stack: {', '.join(stack_hits[:5])}")
    if role_hits:
        reasons.append(f"Matches a target role: {', '.join(role_hits[:3])}")
    if not stack_hits and not role_hits:
        reasons.append("No strong keyword overlap found with your profile")

    fit_score = round(min(100, stack_score + role_score + salary_score))
    if red_flags:
        fit_score = max(0, fit_score - 15 * len(red_flags))

    return {
        "fit_score": fit_score,
        "reasons": reasons,
        "red_flags": red_flags,
        "llm_powered": False,
    }
