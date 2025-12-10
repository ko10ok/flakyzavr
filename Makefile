PROJECT_NAME=flakyzavr

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
	git tag v${VERSION}

.PHONY: tag-beta
tag-beta:
	@echo "Creating next beta tag for version ${VERSION}"
	@LAST_BETA=$$(git tag -l "v${VERSION}b*" | grep -E "v${VERSION}b[0-9]+$$" | sort -V | tail -n 1); \
	if [ -z "$$LAST_BETA" ]; then \
		NEXT_BETA="v${VERSION}b1"; \
		echo "No existing beta tags found. Creating: $$NEXT_BETA"; \
	else \
		BETA_NUM=$$(echo $$LAST_BETA | sed -E 's/.*b([0-9]+)/\1/'); \
		NEXT_NUM=$$((BETA_NUM + 1)); \
		NEXT_BETA="v${VERSION}b$$NEXT_NUM"; \
		echo "Last beta tag: $$LAST_BETA"; \
		echo "Creating next beta tag: $$NEXT_BETA"; \
	fi; \
	git tag $$NEXT_BETA && echo "✓ Tag $$NEXT_BETA created successfully (PyPI version: ${VERSION}b$$NEXT_NUM)"

.PHONY: tag-alpha
tag-alpha:
	@echo "Creating next alpha tag for version ${VERSION}"
	@LAST_ALPHA=$$(git tag -l "v${VERSION}a*" | grep -E "v${VERSION}a[0-9]+$$" | sort -V | tail -n 1); \
	if [ -z "$$LAST_ALPHA" ]; then \
		NEXT_ALPHA="v${VERSION}a1"; \
		echo "No existing alpha tags found. Creating: $$NEXT_ALPHA"; \
	else \
		ALPHA_NUM=$$(echo $$LAST_ALPHA | sed -E 's/.*a([0-9]+)/\1/'); \
		NEXT_NUM=$$((ALPHA_NUM + 1)); \
		NEXT_ALPHA="v${VERSION}a$$NEXT_NUM"; \
		echo "Last alpha tag: $$LAST_ALPHA"; \
		echo "Creating next alpha tag: $$NEXT_ALPHA"; \
	fi; \
	git tag $$NEXT_ALPHA && echo "✓ Tag $$NEXT_ALPHA created successfully (PyPI version: ${VERSION}a$$NEXT_NUM)"

.PHONY: tag-rc
tag-rc:
	@echo "Creating next RC tag for version ${VERSION}"
	@LAST_RC=$$(git tag -l "v${VERSION}rc*" | grep -E "v${VERSION}rc[0-9]+$$" | sort -V | tail -n 1); \
	if [ -z "$$LAST_RC" ]; then \
		NEXT_RC="v${VERSION}rc1"; \
		echo "No existing RC tags found. Creating: $$NEXT_RC"; \
	else \
		RC_NUM=$$(echo $$LAST_RC | sed -E 's/.*rc([0-9]+)/\1/'); \
		NEXT_NUM=$$((RC_NUM + 1)); \
		NEXT_RC="v${VERSION}rc$$NEXT_NUM"; \
		echo "Last RC tag: $$LAST_RC"; \
		echo "Creating next RC tag: $$NEXT_RC"; \
	fi; \
	git tag $$NEXT_RC && echo "✓ Tag $$NEXT_RC created successfully (PyPI version: ${VERSION}rc$$NEXT_NUM)"

.PHONY: push-tags
push-tags:
	@echo "Pushing all tags to origin..."
	git push origin --tags

.PHONY: show-tags
show-tags:
	@echo "Tags for version ${VERSION}:"
	@git tag -l "v${VERSION}*" | sort -V


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
