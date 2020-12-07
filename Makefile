.DEFAULT_GOAL := install-test
black = black -S -l 120 --target-version py38

.PHONY: install
install:
	pip install --progress-bar off -U setuptools pip
	pip install --progress-bar off -r requirements.txt

.PHONY: install-dev
install-dev: install
	pip install --progress-bar off -r test_requirements.txt

.PHONY: install-others
install-others:
	yarn install

.PHONY: format
format:
	isort DungeonFinder
	$(black) DungeonFinder

.PHONY: lint
lint:
	yarn run lint
	flake8 DungeonFinder
	isort --check-only DungeonFinder
	$(black) --check DungeonFinder


.PHONY: test
test:
	pytest --maxfail=8 -n8 --cov=DungeonFinder --cov-report term:skip-covered --durations 20

.PHONY: reset-db
reset-db:
	psql -h localhost -U postgres -c "DROP DATABASE IF EXISTS dungeonfinder"
	psql -h localhost -U postgres -c "CREATE DATABASE dungeonfinder"
