import json

from agent_jobs.config.profile import save_profile
from agent_jobs.llm_client import call_llm, has_llm_keys

FIELD_PROMPTS = [
    ("roles", "Target roles, comma-separated (e.g. Full Stack Developer, Frontend Developer)"),
    ("tech_stack", "Tech stack, comma-separated (e.g. React, Next.js, Python, Django)"),
    ("salary_min_usd", "Minimum salary in USD/month"),
    ("salary_max_usd", "Maximum salary in USD/month"),
    ("timezone", "Your timezone (e.g. UTC+5)"),
    ("preferred_company_size", "Preferred company size (e.g. startup, mid-size, enterprise)"),
    ("remote_preference", "Remote preference (fully_remote, hybrid_ok)"),
    ("no_go", "No-go dealbreakers, comma-separated (e.g. PHP only, no equity)"),
]

LIST_FIELDS = {"roles", "tech_stack", "no_go"}
INT_FIELDS = {"salary_min_usd", "salary_max_usd"}

CV_PARSE_PROMPT = """Extract a candidate profile from this CV/resume text.

CV TEXT:
{cv_text}

Respond with ONLY valid JSON, no markdown fences, in this exact shape:
{{
  "roles": ["<target role>", ...],
  "tech_stack": ["<skill/tech>", ...],
  "salary_min_usd": <int or null>,
  "salary_max_usd": <int or null>,
  "timezone": "<best guess or empty string>",
  "preferred_company_size": "<best guess or empty string>",
  "remote_preference": "fully_remote",
  "no_go": []
}}
"""


def _extract_cv_text(cv_path: str) -> str:
    from pypdf import PdfReader

    if cv_path.lower().endswith(".pdf"):
        reader = PdfReader(cv_path)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    with open(cv_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def _interactive_prompt() -> dict:
    profile = {}
    for field, prompt in FIELD_PROMPTS:
        raw = input(f"{prompt}: ").strip()
        if field in LIST_FIELDS:
            profile[field] = [v.strip() for v in raw.split(",") if v.strip()]
        elif field in INT_FIELDS:
            profile[field] = int(raw) if raw else None
        else:
            profile[field] = raw
    return profile


def setup(cv_path: str | None = None) -> None:
    profile = None

    if cv_path and has_llm_keys():
        try:
            cv_text = _extract_cv_text(cv_path)
            raw = call_llm(CV_PARSE_PROMPT.format(cv_text=cv_text[:8000]), max_tokens=800)
            profile = json.loads(raw)
            print("[setup] Parsed profile from CV via LLM. Review agent_jobs/config/profile.json and edit as needed.")
        except Exception as error:
            print(f"[setup] LLM CV parsing failed ({error}), falling back to interactive prompts")

    if profile is None:
        print("[setup] No LLM keys configured (or no --cv given) — answering profile questions interactively.")
        profile = _interactive_prompt()

    save_profile(profile)
    print("[setup] Saved agent_jobs/config/profile.json")
