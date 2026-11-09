PY ?= .venv/bin/python
ROBOT = $(PY) -m robot --pythonpath . --loglevel DEBUG:INFO

.PHONY: install db-up db-down lint pytest robot-api robot-ui robot-etl smoke all

install:
	python3 -m venv .venv && $(PY) -m pip install -r requirements.txt

db-up:
	docker compose up -d --wait

db-down:
	docker compose down -v

lint:
	$(PY) -m ruff check framework tests robot/libraries

pytest:
	$(PY) -m pytest --junitxml=results/pytest/junit.xml

robot-api:
	$(ROBOT) --outputdir results/robot-api robot/tests/api

robot-ui:
	$(ROBOT) --outputdir results/robot-ui robot/tests/ui

robot-etl:
	$(ROBOT) --outputdir results/robot-etl robot/tests/etl

smoke:
	$(PY) -m pytest -m smoke
	$(ROBOT) --include smoke --outputdir results/robot-smoke robot/tests

all: lint pytest robot-api robot-ui robot-etl
