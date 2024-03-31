PROJECT_NAME=vedro_jira_failed_reporter

.PHONY: install-deps
install-deps:
	pip3 install --quiet --upgrade pip
	pip3 install --quiet -r requirements.txt -r requirements-dev.txt

.PHONY: install-local
install-local: install-deps
	pip3 install . --force-reinstall

.PHONY: build
build:
	pip3 install --quiet --upgrade pip
	pip3 install --quiet --upgrade setuptools wheel twine
	python3 setup.py sdist bdist_wheel

.PHONY: publish
publish:
	twine upload dist/*

.PHONY: tag
tag:
	git tag v`cat ${PROJECT_NAME}/version`

.PHONY: check-types
check-types:
	python3 -m mypy ${PROJECT_NAME} --strict

.PHONY: check-imports
check-imports:
	python3 -m isort --sl ${PROJECT_NAME} ${PROJECT_NAME} --check-only

.PHONY: sort-imports
sort-imports:
	python3 -m isort --sl ${PROJECT_NAME} ${PROJECT_NAME}

.PHONY: check-style
check-style:
	python3 -m flake8 ${PROJECT_NAME} ${PROJECT_NAME}

.PHONY: lint
lint: check-types check-style check-imports

.PHONY: all-in-docker
all-in-docker:
	docker run -v `pwd`:/tmp/app -w /tmp/app python:$(or $(PYTHON_VERSION),3.10) make install-deps lint
