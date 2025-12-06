export COMPOSE_FILE ?= docker-compose.yml
export VERSION := $(shell git describe --tags --exact-match 2>/dev/null || echo beta)
export PYTHON_VERSION ?= 3.10

.PHONY: down
down:
	rm up || true
	rm dep || true
	docker-compose down || true

build:
	docker-compose build --build-arg PYTHON_VERSION=${PYTHON_VERSION}
	echo "" > build

up: build
	docker-compose up -d
	echo "" > up

deps: up
	docker-compose exec ${CI_DC_DISABLE_TTY} e2e python3 -m venv /venv
	docker-compose exec ${CI_DC_DISABLE_TTY} e2e uv pip sync -p /venv/bin/python3 requirements.txt
	docker-compose exec ${CI_DC_DISABLE_TTY} e2e uv pip install -p /venv/bin/python3 /flakyzavr
	echo "" > deps

.PHONY: e2e-run
e2e-run: up deps
	docker-compose exec ${CI_DC_DISABLE_TTY} e2e /venv/bin/python3 -m vedro run $(args)

.PHONY: e2e-fix-imports
e2e-fix-imports:
	@docker compose exec e2e sh -c 'python3 -m autoflake --remove-all-unused-imports --ignore-init-module-imports --recursive --in-place .'
	@docker compose exec e2e sh -c 'python3 -m isort .'
