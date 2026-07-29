"""Shared SQLite schema. agent-jobs owns migrations; agent-ats's backend
runs the same CREATE TABLE IF NOT EXISTS DDL read-only, so the dashboard
never 500s just because agent-jobs hasn't run yet.
"""

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS jobs (
    id TEXT PRIMARY KEY,
    source TEXT NOT NULL,
    source_native_id TEXT,
    title TEXT NOT NULL,
    company TEXT,
    company_url TEXT,
    location TEXT,
    remote_type TEXT,
    salary_min_usd INTEGER,
    salary_max_usd INTEGER,
    tags TEXT,
    jd_text TEXT NOT NULL,
    apply_url TEXT NOT NULL,
    posted_at TEXT,
    fetched_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    raw_json TEXT
);
CREATE INDEX IF NOT EXISTS idx_jobs_source ON jobs(source);
CREATE INDEX IF NOT EXISTS idx_jobs_posted_at ON jobs(posted_at);

CREATE TABLE IF NOT EXISTS scored (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id TEXT NOT NULL REFERENCES jobs(id),
    fit_score INTEGER NOT NULL,
    reasons TEXT,
    red_flags TEXT,
    llm_powered INTEGER NOT NULL,
    profile_snapshot TEXT,
    scored_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_scored_job_id ON scored(job_id, scored_at DESC);

CREATE TABLE IF NOT EXISTS selected (
    job_id TEXT PRIMARY KEY REFERENCES jobs(id),
    status TEXT NOT NULL,
    cover_note TEXT,
    cover_note_generated_at TEXT,
    selected_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS applied (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id TEXT NOT NULL REFERENCES jobs(id),
    status TEXT NOT NULL,
    applied_at TEXT NOT NULL,
    notes TEXT,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS source_rate_limits (
    source TEXT PRIMARY KEY,
    window_start TEXT NOT NULL,
    window_seconds INTEGER NOT NULL,
    calls_made INTEGER NOT NULL DEFAULT 0,
    call_budget INTEGER NOT NULL,
    updated_at TEXT NOT NULL
);
"""


def run_migrations(conn) -> None:
    conn.executescript(SCHEMA_SQL)
    conn.commit()
