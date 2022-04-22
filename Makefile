.PHONY: all
all: install

.PHONY: ci
ci: format check

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

.PHONY: format
format: install
	poetry run autoflake . --in-place --remove-all-unused-imports
	poetry run isort .
	poetry run black .

.PHONY: check
check: install
	poetry run mypy .

# RUN

.PHONY: run
run: install
	status=1; \
	while [ $$status -eq 1 ] ; do \
		poetry run python app.py; \
		status=$$?; \
		sleep 1; \
	done; \

.PHONY: serve
serve:
	status=1; \
	while [ $$status -eq 1 ] ; do \
		git pull; \
		poetry install --no-dev; \
		poetry run flask run; \
		status=$$?; \
		sleep 1; \
	done; \

# CLEANUP

.PHONY: clean
clean:
	rm -rf data

.PHONY: clean-all
clean-all: clean
	rm -rf .venv
