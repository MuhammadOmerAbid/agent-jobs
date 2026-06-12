import json
from shared.llm import ask
from agent_jobs.db import get_job

_SYSTEM = """You are a career coach. Write a short, tailored cover note (150-200 words) for the job below,
based on the candidate profile. Be specific, honest, and professional.
Also suggest 2-3 CV bullet tweaks as a JSON array under the key 'cv_tweaks'.
Return JSON: {\"cover_note\": \"...\", \"cv_tweaks\": [...]}"""


def generate_cover(job_id: int, profile: dict) -> dict:
    job = get_job(job_id)
    if job is None:
        return {"error": f"Job {job_id} not found"}
    prompt = f"Profile:\n{json.dumps(profile, indent=2)}\n\nJob:\nTitle: {job['title']}\nCompany: {job['company']}\nDescription: {job['description'][:1200]}"
    raw = ask(system=_SYSTEM, user=prompt, max_tokens=512)
    try:
        return json.loads(raw)
    except Exception:
        return {"cover_note": raw, "cv_tweaks": []}
