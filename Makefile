install:
	python -m venv venv
	venv\Scripts\pip install -r requirements.txt

run:
	python main.py

lint:
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

