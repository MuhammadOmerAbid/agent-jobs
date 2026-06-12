import os
import sqlite3
from shared.db import execute, fetchall, fetchone

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "jobs.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


def init_db() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT,
                title TEXT,
                company TEXT,
                url TEXT UNIQUE,
                description TEXT,
                salary TEXT,
                fetched_at TEXT DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS scored (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id INTEGER UNIQUE,
                fit_pct INTEGER,
                pros TEXT,
                red_flags TEXT,
                scored_at TEXT DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS selected (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id INTEGER UNIQUE,
                cover_note TEXT,
                selected_at TEXT DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS applied (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id INTEGER,
                applied_at TEXT DEFAULT (datetime('now'))
            );
        """)


def save_job(source: str, title: str, company: str, url: str, description: str, salary: str) -> int | None:
    try:
        execute(DB_PATH, 
            "INSERT INTO jobs (source, title, company, url, description, salary) VALUES (?,?,?,?,?,?)",
            (source, title, company, url, description, salary))
        row = fetchone(DB_PATH, "SELECT last_insert_rowid() AS id")
        return row["id"]
    except Exception:
        return None


def get_unscored_jobs() -> list[dict]:
    return fetchall(DB_PATH, 
        "SELECT j.* FROM jobs j LEFT JOIN scored s ON j.id = s.job_id WHERE s.id IS NULL")


def save_score(job_id: int, fit_pct: int, pros: str, red_flags: str) -> None:
    execute(DB_PATH,
        "INSERT OR REPLACE INTO scored (job_id, fit_pct, pros, red_flags) VALUES (?,?,?,?)",
        (job_id, fit_pct, pros, red_flags))


def get_top_jobs(limit: int = 5) -> list[dict]:
    return fetchall(DB_PATH,
        """SELECT j.*, s.fit_pct, s.pros, s.red_flags
           FROM jobs j JOIN scored s ON j.id = s.job_id
           ORDER BY s.fit_pct DESC LIMIT ?""",
        (limit,))


def get_job(job_id: int) -> dict | None:
    return fetchone(DB_PATH, "SELECT * FROM jobs WHERE id = ?", (job_id,))
