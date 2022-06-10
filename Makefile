.PHONY: all
all: install

.PHONY: ci
ci: check test

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
check: install format
ifdef CI
	git diff --exit-code
endif
	poetry run mypy $(PACKAGES)

.PHONY: test
test: test-unit test-e2e

.PHONY: test-unit
test-unit: install
	poetry run pytest

.PHONY: test-e2e
test-e2e: install
ifdef CI
ifdef HONCHO_PROCESS_NAME
	poetry run pomace exec tests/e2e.py --headless
else
	poetry run honcho start --procfile tests/Procfile
endif
else
	poetry run pomace exec tests/e2e.py
endif

.PHONY: dev
dev: install
	cp tests/files/test.yml data/games
	poetry run ptw --nobeep --beforerun "clear" --onpass "echo && make check && echo"

# RUN

.PHONY: run
run: install .envrc
	@ echo "poetry run python run.py"
	@ status=1; \
	while [ $$status -eq 1 ] ; do \
		poetry run python run.py; \
		status=$$?; \
		sleep 1; \
	done; \

.envrc:
	echo "export SIZE=5" >> $@
	echo "export PLAYERS=2" >> $@
	echo "export SHARED=false" >> $@
	- direnv allow

.PHONY: serve
serve:
ifndef CI
	git pull
	poetry install --no-dev
endif
ifndef PYTHONANYWHERE_DOMAIN
	poetry run gunicorn --workers 4 --bind 0.0.0.0:5000 app.views:app
endif

# CLEAN

.PHONY: clean
clean:
	rm -rf data

.PHONY: clean-all
clean-all: clean
	rm -rf .venv
