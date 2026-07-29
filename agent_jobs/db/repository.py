import json
from datetime import datetime, timezone
from typing import Any, Optional

from agent_jobs.db.connection import get_connection
from agent_jobs.db.ids import make_job_id


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def upsert_job(posting: dict[str, Any]) -> str:
    """posting must have: source, source_native_id, title, company, company_url,
    location, remote_type, salary_min_usd, salary_max_usd, tags (list),
    jd_text, apply_url, posted_at, raw_json (dict/str)."""
    job_id = make_job_id(posting["source"], posting["source_native_id"])
    now = _now()
    tags_json = json.dumps(posting.get("tags") or [])
    raw = posting.get("raw_json")
    raw_json = raw if isinstance(raw, str) else json.dumps(raw or {})

    conn = get_connection()
    try:
        existing = conn.execute("SELECT id FROM jobs WHERE id = ?", (job_id,)).fetchone()
        if existing:
            conn.execute(
                """UPDATE jobs SET title=?, company=?, company_url=?, location=?,
                   remote_type=?, salary_min_usd=?, salary_max_usd=?, tags=?,
                   jd_text=?, apply_url=?, posted_at=?, updated_at=?, raw_json=?
                   WHERE id=?""",
                (
                    posting["title"], posting.get("company"), posting.get("company_url"),
                    posting.get("location"), posting.get("remote_type"),
                    posting.get("salary_min_usd"), posting.get("salary_max_usd"),
                    tags_json, posting["jd_text"], posting["apply_url"],
                    posting.get("posted_at"), now, raw_json, job_id,
                ),
            )
        else:
            conn.execute(
                """INSERT INTO jobs (id, source, source_native_id, title, company,
                   company_url, location, remote_type, salary_min_usd, salary_max_usd,
                   tags, jd_text, apply_url, posted_at, fetched_at, updated_at, raw_json)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    job_id, posting["source"], posting["source_native_id"], posting["title"],
                    posting.get("company"), posting.get("company_url"), posting.get("location"),
                    posting.get("remote_type"), posting.get("salary_min_usd"),
                    posting.get("salary_max_usd"), tags_json, posting["jd_text"],
                    posting["apply_url"], posting.get("posted_at"), now, now, raw_json,
                ),
            )
        conn.commit()
        return job_id
    finally:
        conn.close()


def insert_score(job_id: str, fit_score: int, reasons: list[str], red_flags: list[str],
                  llm_powered: bool, profile_snapshot: dict) -> None:
    conn = get_connection()
    try:
        conn.execute(
            """INSERT INTO scored (job_id, fit_score, reasons, red_flags, llm_powered,
               profile_snapshot, scored_at) VALUES (?,?,?,?,?,?,?)""",
            (
                job_id, fit_score, json.dumps(reasons), json.dumps(red_flags),
                1 if llm_powered else 0, json.dumps(profile_snapshot), _now(),
            ),
        )
        conn.commit()
    finally:
        conn.close()


def get_jobs(filters: Optional[dict] = None) -> list[dict]:
    filters = filters or {}
    conn = get_connection()
    try:
        query = """
            SELECT j.*, s.fit_score, s.reasons, s.red_flags, s.llm_powered, s.scored_at
            FROM jobs j
            LEFT JOIN (
                SELECT job_id, fit_score, reasons, red_flags, llm_powered, scored_at,
                       ROW_NUMBER() OVER (PARTITION BY job_id ORDER BY scored_at DESC) rn
                FROM scored
            ) s ON s.job_id = j.id AND s.rn = 1
            WHERE 1=1
        """
        params: list[Any] = []
        if filters.get("source"):
            query += " AND j.source = ?"
            params.append(filters["source"])
        if filters.get("min_fit_score") is not None:
            query += " AND s.fit_score >= ?"
            params.append(filters["min_fit_score"])
        query += " ORDER BY j.posted_at DESC LIMIT ? OFFSET ?"
        params.append(filters.get("limit", 50))
        params.append(filters.get("offset", 0))
        rows = conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_job(job_id: str) -> Optional[dict]:
    conn = get_connection()
    try:
        row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
        if not row:
            return None
        job = dict(row)
        score = conn.execute(
            "SELECT * FROM scored WHERE job_id = ? ORDER BY scored_at DESC LIMIT 1",
            (job_id,),
        ).fetchone()
        job["score"] = dict(score) if score else None
        return job
    finally:
        conn.close()


def existing_job_ids(job_ids: list[str]) -> set[str]:
    if not job_ids:
        return set()
    conn = get_connection()
    try:
        placeholders = ",".join("?" for _ in job_ids)
        rows = conn.execute(
            f"SELECT id FROM jobs WHERE id IN ({placeholders})", job_ids
        ).fetchall()
        return {row["id"] for row in rows}
    finally:
        conn.close()


# --- rate limit helpers ---

def get_rate_limit_state(source: str) -> Optional[dict]:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM source_rate_limits WHERE source = ?", (source,)
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def upsert_rate_limit_state(source: str, window_start: str, window_seconds: int,
                             calls_made: int, call_budget: int) -> None:
    conn = get_connection()
    try:
        conn.execute(
            """INSERT INTO source_rate_limits (source, window_start, window_seconds,
               calls_made, call_budget, updated_at) VALUES (?,?,?,?,?,?)
               ON CONFLICT(source) DO UPDATE SET
                 window_start=excluded.window_start,
                 window_seconds=excluded.window_seconds,
                 calls_made=excluded.calls_made,
                 call_budget=excluded.call_budget,
                 updated_at=excluded.updated_at""",
            (source, window_start, window_seconds, calls_made, call_budget, _now()),
        )
        conn.commit()
    finally:
        conn.close()
