import json

from agent_jobs.llm_client import call_llm, has_llm_keys
from agent_jobs.scoring.rule_based import score_job_rule_based

PROMPT_TEMPLATE = """You are scoring how well a remote job posting fits a candidate's profile.

CANDIDATE PROFILE (JSON):
{profile_json}

JOB POSTING:
Title: {title}
Company: {company}
Location: {location}
Tags: {tags}
Description:
{jd_text}

Score the fit from 0-100 and explain why. Consider tech stack overlap, role match,
salary range fit, remote preference, and any "no_go" red flags from the profile.

Respond with ONLY valid JSON, no markdown fences, in this exact shape:
{{"fit_score": <int 0-100>, "reasons": ["<short reason>", ...], "red_flags": ["<short red flag>", ...]}}
"""


def score_job(job: dict, profile: dict) -> dict:
    if not has_llm_keys():
        return score_job_rule_based(job, profile)

    prompt = PROMPT_TEMPLATE.format(
        profile_json=json.dumps(profile),
        title=job.get("title", ""),
        company=job.get("company", ""),
        location=job.get("location", ""),
        tags=", ".join(job.get("tags") or []),
        jd_text=(job.get("jd_text") or "")[:6000],
    )

    try:
        raw = call_llm(prompt, prefer_fast=True, max_tokens=600)
        parsed = json.loads(raw)
        return {
            "fit_score": int(parsed["fit_score"]),
            "reasons": list(parsed.get("reasons", [])),
            "red_flags": list(parsed.get("red_flags", [])),
            "llm_powered": True,
        }
    except Exception as error:
        print(f"[scoring] LLM scoring failed ({error}), falling back to rule-based")
        return score_job_rule_based(job, profile)
