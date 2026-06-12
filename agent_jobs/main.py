"""agent-jobs CLI

Usage:
  python agent_jobs/main.py setup --cv path/to/cv.pdf
  python agent_jobs/main.py run
  python agent_jobs/main.py schedule
  python agent_jobs/main.py cover --job-id 42
"""
import sys
import json
import os
from agent_jobs.db import init_db, get_top_jobs
from agent_jobs.fetcher import fetch_all
from agent_jobs.scorer import score_all
from agent_jobs.cover import generate_cover
from shared.approval import notify

PROFILE_PATH = os.path.join(os.path.dirname(__file__), "config", "profile.json")


def load_profile() -> dict:
    with open(PROFILE_PATH) as f:
        return json.load(f)


def cmd_run() -> None:
    init_db()
    profile = load_profile()
    print("Fetching jobs...")
    counts = fetch_all()
    print(f"Fetched: {counts}")
    print("Scoring jobs...")
    scored = score_all(profile)
    print(f"Scored {scored} new jobs.")
    top = get_top_jobs(5)
    if not top:
        print("No top matches found.")
        return
    lines = ["*Daily Job Digest*\n"]
    for i, job in enumerate(top, 1):
        icon = "✅" if job["fit_pct"] >= 80 else "⚠️"
        lines.append(
            f"{i}. {job['title']} @ {job['company']}\n"
            f"   Fit: {job['fit_pct']}% {icon}\n"
            f"   Pros: {job['pros']}\n"
            f"   Red flags: {job['red_flags'] or 'None'}\n"
            f"   {job['url']}"
        )
    notify("\n".join(lines))
    print("Digest sent to Telegram.")


def cmd_cover(job_id: int) -> None:
    init_db()
    profile = load_profile()
    result = generate_cover(job_id, profile)
    print("\n--- Cover Note ---")
    print(result.get("cover_note", ""))
    tweaks = result.get("cv_tweaks", [])
    if tweaks:
        print("\n--- CV Tweaks ---")
        for t in tweaks:
            print(f"  - {t}")


def cmd_schedule() -> None:
    from apscheduler.schedulers.blocking import BlockingScheduler
    from agent_jobs.config.schedule import SCHEDULE_HOUR, SCHEDULE_MINUTE
    init_db()
    sched = BlockingScheduler()
    sched.add_job(cmd_run, trigger="cron", hour=SCHEDULE_HOUR, minute=SCHEDULE_MINUTE)
    print(f"Scheduler started: daily at {SCHEDULE_HOUR:02d}:{SCHEDULE_MINUTE:02d}")
    sched.start()


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)
    cmd = args[0]
    if cmd == "run":
        cmd_run()
    elif cmd == "schedule":
        cmd_schedule()
    elif cmd == "cover":
        if "--job-id" not in args:
            print("Usage: python agent_jobs/main.py cover --job-id <id>")
            sys.exit(1)
        job_id = int(args[args.index("--job-id") + 1])
        cmd_cover(job_id)
    else:
        print(__doc__)
        sys.exit(1)
