import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv

from agent_jobs.db.schema import run_migrations

load_dotenv()

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "jobs.db"


def get_connection() -> sqlite3.Connection:
    db_path = os.environ.get("JOBS_DB_PATH", str(DEFAULT_DB_PATH))
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA busy_timeout=5000;")
    run_migrations(conn)
    return conn
