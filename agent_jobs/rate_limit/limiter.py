from datetime import datetime, timedelta, timezone

from agent_jobs.db.repository import get_rate_limit_state, upsert_rate_limit_state
from agent_jobs.rate_limit.budgets import budget_for


def _now() -> datetime:
    return datetime.now(timezone.utc)


def can_fetch(source: str, cost: int = 1) -> bool:
    """Returns True if `source` still has budget left in its current window,
    resetting the window if it has expired."""
    call_budget, window_seconds = budget_for(source)
    state = get_rate_limit_state(source)

    if state is None:
        return True

    window_start = datetime.fromisoformat(state["window_start"])
    if _now() - window_start > timedelta(seconds=state["window_seconds"]):
        return True  # window has expired, will reset on next record_call

    return state["calls_made"] + cost <= call_budget


def record_call(source: str, cost: int = 1) -> None:
    call_budget, window_seconds = budget_for(source)
    state = get_rate_limit_state(source)
    now = _now()

    if state is None:
        upsert_rate_limit_state(source, now.isoformat(), window_seconds, cost, call_budget)
        return

    window_start = datetime.fromisoformat(state["window_start"])
    if now - window_start > timedelta(seconds=state["window_seconds"]):
        upsert_rate_limit_state(source, now.isoformat(), window_seconds, cost, call_budget)
    else:
        upsert_rate_limit_state(
            source, state["window_start"], window_seconds, state["calls_made"] + cost, call_budget
        )


def reset_at(source: str) -> str | None:
    state = get_rate_limit_state(source)
    if state is None:
        return None
    window_start = datetime.fromisoformat(state["window_start"])
    reset = window_start + timedelta(seconds=state["window_seconds"])
    return reset.isoformat()
