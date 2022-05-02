.PHONY: all
all: install

.PHONY: ci
ci: format check test

# INSTALL

BACKEND_DEPENDENCIES := .venv/.flag

.PHONY: install
install: $(BACKEND_DEPENDENCIES)

$(BACKEND_DEPENDENCIES): poetry.lock
	@ poetry config virtualenvs.in-project true
	poetry install
	@ touch $@

ifndef CI
poetry.lock: pyproject.toml
	poetry lock --no-update
	@ touch $@
endif

# TEST

PACKAGES = app tests

.PHONY: format
format: install
	poetry run autoflake --recursive $(PACKAGES) --in-place --remove-all-unused-imports
	poetry run isort $(PACKAGES)
	poetry run black $(PACKAGES)

.PHONY: check
check: install
	poetry run mypy $(PACKAGES)

.PHONY: test
test: install
	poetry run pomace exec tests/e2e.py --headless

# RUN

.PHONY: run
run: install
	@ echo "poetry run python run.py"
	@ status=1; \
	while [ $$status -eq 1 ] ; do \
		poetry run python run.py; \
		status=$$?; \
		sleep 1; \
	done; \

.PHONY: serve
serve:
	git pull
	poetry install --no-dev
	poetry run gunicorn --workers 4 --bind 0.0.0.0:5000 app.views:app

# CLEANUP

.PHONY: clean
clean:
	rm -rf data

.PHONY: clean-all
clean-all: clean
	rm -rf .venv
