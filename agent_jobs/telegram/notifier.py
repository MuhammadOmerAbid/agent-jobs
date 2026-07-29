"""Optional, secondary notifier — deferred fast-follow (see project plan).

The in-app /jobs dashboard in agent-ats's frontend is the primary interface;
this module, when built, should just post a short "N new matches" ping per
run with a deep link to https://<frontend-host>/jobs/{id} per job, reusing
TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID env vars. Not wired into the CLI yet.
"""


def send_digest(jobs: list[dict]) -> None:
    raise NotImplementedError("Telegram digest is deferred — see project plan.")
