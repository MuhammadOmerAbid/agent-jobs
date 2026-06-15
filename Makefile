.PHONY: install run schedule cover test lint

install:
	pip install -r requirements.txt

run:
	python agent_jobs/main.py run

schedule:
	python agent_jobs/main.py schedule

cover:
	python agent_jobs/main.py cover --job-id $(ID)

test:
	pytest tests/ -v

lint:
	python -m py_compile agent_jobs/main.py agent_jobs/db.py agent_jobs/fetcher.py agent_jobs/scorer.py agent_jobs/cover.py
