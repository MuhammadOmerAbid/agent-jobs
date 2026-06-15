import os
import sys
import sqlite3
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def test_init_db(tmp_path, monkeypatch):
    import agent_jobs.db as db_mod
    test_db = str(tmp_path / "jobs.db")
    monkeypatch.setattr(db_mod, "DB_PATH", test_db)
    db_mod.init_db()
    conn = sqlite3.connect(test_db)
    tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
    conn.close()
    assert {"jobs", "scored", "selected", "applied"}.issubset(tables)


def test_save_and_get_job(tmp_path, monkeypatch):
    import agent_jobs.db as db_mod
    test_db = str(tmp_path / "jobs.db")
    monkeypatch.setattr(db_mod, "DB_PATH", test_db)
    db_mod.init_db()
    job_id = db_mod.save_job(
        source="remoteok",
        title="Senior Frontend Dev",
        company="Acme Inc",
        url="https://example.com/job/1",
        description="React, Next.js, remote",
        salary="$5k-$7k",
    )
    assert job_id is not None
    job = db_mod.get_job(job_id)
    assert job["title"] == "Senior Frontend Dev"
    assert job["company"] == "Acme Inc"
