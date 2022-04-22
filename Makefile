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
	poetry run python app.py

.PHONY: serve
serve:
	status=1; \
	while [ $$status -eq 1 ] ; do \
		git pull; \
		make install; \
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
