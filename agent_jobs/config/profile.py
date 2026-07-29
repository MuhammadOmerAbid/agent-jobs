import json
from pathlib import Path

PROFILE_PATH = Path(__file__).resolve().parent / "profile.json"

DEFAULT_PROFILE = {
    "roles": [],
    "tech_stack": [],
    "salary_min_usd": None,
    "salary_max_usd": None,
    "timezone": "",
    "preferred_company_size": "",
    "remote_preference": "fully_remote",
    "no_go": [],
}


def load_profile() -> dict:
    if not PROFILE_PATH.exists():
        raise FileNotFoundError(
            f"No profile found at {PROFILE_PATH}. Run `python agent_jobs/main.py setup --cv <path>` first."
        )
    with open(PROFILE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_profile(profile: dict) -> None:
    merged = {**DEFAULT_PROFILE, **profile}
    PROFILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(PROFILE_PATH, "w", encoding="utf-8") as f:
        json.dump(merged, f, indent=2)


def profile_exists() -> bool:
    return PROFILE_PATH.exists()
