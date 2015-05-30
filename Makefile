# Project settings
PROJECT := GridCommand
PACKAGE := gridcommand
SOURCES := Makefile setup.py $(shell find $(PACKAGE) -name '*.py')
EGG_INFO := $(subst -,_,$(PROJECT)).egg-info

# Python settings
ifndef TRAVIS
	PYTHON_MAJOR := 3
	PYTHON_MINOR := 4
endif

# Test settings
UNIT_TEST_COVERAGE := 83
INTEGRATION_TEST_COVERAGE := 44
COMBINED_TEST_COVERAGE := 83

# System paths
PLATFORM := $(shell python -c 'import sys; print(sys.platform)')
ifneq ($(findstring win32, $(PLATFORM)), )
	WINDOWS := 1
	SYS_PYTHON_DIR := C:\\Python$(PYTHON_MAJOR)$(PYTHON_MINOR)
	SYS_PYTHON := $(SYS_PYTHON_DIR)\\python.exe
	SYS_VIRTUALENV := $(SYS_PYTHON_DIR)\\Scripts\\virtualenv.exe
	# https://bugs.launchpad.net/virtualenv/+bug/449537
	export TCL_LIBRARY=$(SYS_PYTHON_DIR)\\tcl\\tcl8.5
else
	ifneq ($(findstring darwin, $(PLATFORM)), )
		MAC := 1
	else
		LINUX := 1
	endif
	SYS_PYTHON := python$(PYTHON_MAJOR)
	ifdef PYTHON_MINOR
		SYS_PYTHON := $(SYS_PYTHON).$(PYTHON_MINOR)
	endif
	SYS_VIRTUALENV := virtualenv
endif

# virtualenv paths
ENV := env
ifneq ($(findstring win32, $(PLATFORM)), )
	BIN := $(ENV)/Scripts
	OPEN := cmd /c start
else
	BIN := $(ENV)/bin
	ifneq ($(findstring cygwin, $(PLATFORM)), )
		OPEN := cygstart
	else
		OPEN := open
	endif
endif

# virtualenv executables
PYTHON := $(BIN)/python
PIP := $(BIN)/pip
EASY_INSTALL := $(BIN)/easy_install
RST2HTML := $(PYTHON) $(BIN)/rst2html.py
PDOC := $(PYTHON) $(BIN)/pdoc
PEP8 := $(BIN)/pep8
PEP8RADIUS := $(BIN)/pep8radius
PEP257 := $(BIN)/pep257
PYLINT := $(BIN)/pylint
PYREVERSE := $(BIN)/pyreverse
NOSE := $(BIN)/nosetests
PYTEST := $(BIN)/py.test
COVERAGE := $(BIN)/coverage
SNIFFER := $(BIN)/sniffer

# Flags for PHONY targets
INSTALLED := $(ENV)/.installed
DEPENDS_CI := $(ENV)/.depends-ci
DEPENDS_DEV := $(ENV)/.depends-dev
ALL := $(ENV)/.all

# Main Targets #################################################################

.PHONY: all
all: depends doc $(ALL)
$(ALL): $(SOURCES)
	$(MAKE) check
	touch $(ALL)  # flag to indicate all setup steps were successful

.PHONY: ci
ci: check test tests

.PHONY: run
run: env
	$(PYTHON) main.py --debug

.PHONY: launch
launch: env
	eval "sleep 1; $(OPEN) http://127.0.0.1:5000" &
	$(MAKE) run

.PHONY: run-private
run-private: run

.PHONY: launch-private
launch-private: launch

.PHONY: run-public
run-public: env
	$(PYTHON) main.py --public

.PHONY: launch-public
launch-public: env
	eval "sleep 1; $(OPEN) http://localhost:8000" &
	$(MAKE) run-public

# Development Installation #####################################################

.PHONY: env
env: .virtualenv $(INSTALLED)
$(INSTALLED): Makefile requirements.txt
	VIRTUAL_ENV=$(ENV) $(PIP) install -r requirements.txt
	touch $(INSTALLED)  # flag to indicate package is installed

.PHONY: .virtualenv
.virtualenv: $(PIP)
$(PIP):
	$(SYS_VIRTUALENV) --python $(SYS_PYTHON) $(ENV)
	$(PIP) install --upgrade pip

.PHONY: depends
depends: depends-ci depends-dev

.PHONY: depends-ci
depends-ci: env Makefile $(DEPENDS_CI)
$(DEPENDS_CI): Makefile
	$(PIP) install --upgrade pep8 pep257 pylint coverage pytest pytest-cov pytest-capturelog
	touch $(DEPENDS_CI)  # flag to indicate dependencies are installed

.PHONY: depends-dev
depends-dev: env Makefile $(DEPENDS_DEV)
$(DEPENDS_DEV): Makefile
	$(PIP) install --upgrade pip pep8radius pygments docutils pdoc wheel readme sniffer
ifdef WINDOWS
	$(PIP) install --upgrade pywin32
else ifdef MAC
	$(PIP) install --upgrade pync MacFSEvents
else ifdef LINUX
	$(PIP) install --upgrade pyinotify
endif
	touch $(DEPENDS_DEV)  # flag to indicate dependencies are installed

# Documentation ################################################################

.PHONY: doc
doc: readme apidocs uml

.PHONY: readme
readme: depends-dev README-github.html README-pypi.html
README-github.html: README.md
	pandoc -f markdown_github -t html -o README-github.html README.md
README-pypi.html: README.rst
	$(RST2HTML) README.rst README-pypi.html
README.rst: README.md
	pandoc -f markdown_github -t rst -o README.rst README.md

.PHONY: apidocs
apidocs: depends-dev apidocs/$(PACKAGE)/index.html
apidocs/$(PACKAGE)/index.html: $(SOURCES)
	$(PDOC) --html --overwrite $(PACKAGE) --html-dir apidocs

.PHONY: uml
uml: depends-dev docs/*.png
docs/*.png: $(SOURCES)
	$(PYREVERSE) $(PACKAGE) -p $(PACKAGE) -a 1 -f ALL -o png --ignore test
	- mv -f classes_$(PACKAGE).png docs/classes.png
	- mv -f packages_$(PACKAGE).png docs/packages.png

.PHONY: read
read: doc
	$(OPEN) apidocs/$(PACKAGE)/index.html
	$(OPEN) README-pypi.html
	$(OPEN) README-github.html

# Static Analysis ##############################################################

.PHONY: check
check: pep8 pylint pep257

.PHONY: pep8
pep8: depends-ci
# E501: line too long (checked by PyLint)
# E402: module level import not at the top of file (delayed import for routes)
	$(PEP8) $(PACKAGE) --ignore=E501,E402

.PHONY: pep257
pep257: depends-ci
# D102: docstring missing (checked by PyLint)
# D202: No blank lines allowed *after* function docstring
	$(PEP257) $(PACKAGE) --ignore=D100,D101,D102,D202

.PHONY: pylint
pylint: depends-ci
# C0111: Missing method docstring (warning displayed in editors)
# R0801: Similar lines (checked by Scrutinizer)
	$(PYLINT) $(PACKAGE) --rcfile=.pylintrc --disable=C0111,R0801

.PHONY: fix
fix: depends-dev
	$(PEP8RADIUS) --docformatter --in-place

# Testing ######################################################################

PYTEST_CORE_OPTS := --doctest-modules
PYTEST_COV_OPTS := --cov=$(PACKAGE) --cov-report=term-missing --cov-report=html
PYTEST_CAPTURELOG_OPTS := --log-format="%(name)-25s %(lineno)4d %(levelname)8s: %(message)s"
PYTEST_OPTS := $(PYTEST_CORE_OPTS) $(PYTEST_COV_OPTS) $(PYTEST_CAPTURELOG_OPTS)

.PHONY: test-unit
test-unit: test
.PHONY: test
test: depends-ci .clean-test
	$(PYTEST) $(PYTEST_OPTS) $(PACKAGE)
	$(COVERAGE) report --fail-under=$(UNIT_TEST_COVERAGE) > /dev/null

.PHONY: test-int
test-int: depends-ci .clean-test
	TEST_INTEGRATION=1 $(PYTEST) $(PYTEST_OPTS) tests
	$(COVERAGE) report --fail-under=$(INTEGRATION_TEST_COVERAGE) > /dev/null

.PHONY: test-all
test-all: tests
.PHONY: tests
tests: depends-ci .clean-test
	TEST_INTEGRATION=1 $(PYTEST) $(PYTEST_OPTS) $(PACKAGE) tests
	$(COVERAGE) report --fail-under=$(COMBINED_TEST_COVERAGE) > /dev/null

.PHONY: read-coverage
read-coverage:
	$(OPEN) htmlcov/index.html

.PHONY: watch
watch: depends-dev
	mkdir -p htmlcov && touch htmlcov/index.html && $(MAKE) read-coverage
	$(SNIFFER)

# Cleanup ######################################################################

.PHONY: clean
clean: .clean-dist .clean-test .clean-doc .clean-build
	rm -rf $(ALL)

.PHONY: clean-env
clean-env: clean
	rm -rf $(ENV)

.PHONY: clean-data
clean-data:
	cd data && git clean -fX

.PHONY: clean-all
clean-all: clean clean-env clean-data .clean-workspace

.PHONY: .clean-build
.clean-build:
	find $(PACKAGE) -name '*.pyc' -delete
	find $(PACKAGE) -name '__pycache__' -delete
	rm -rf $(EGG_INFO)

.PHONY: .clean-doc
.clean-doc:
	rm -rf README.rst apidocs *.html docs/*.png

.PHONY: .clean-test
.clean-test:
	rm -rf .coverage htmlcov

.PHONY: .clean-dist
.clean-dist:
	rm -rf dist build

.PHONY: .clean-workspace
.clean-workspace:
	rm -rf *.sublime-workspace

# Release ######################################################################

.PHONY: register
register: doc
	$(PYTHON) setup.py register

.PHONY: dist
dist: check doc test tests
	$(PYTHON) setup.py sdist
	$(PYTHON) setup.py bdist_wheel
	$(MAKE) read

.PHONY: upload
upload: .git-no-changes doc
	$(PYTHON) setup.py register sdist upload
	$(PYTHON) setup.py bdist_wheel upload

.PHONY: .git-no-changes
.git-no-changes:
	@if git diff --name-only --exit-code;         \
	then                                          \
		echo Git working copy is clean...;        \
	else                                          \
		echo ERROR: Git working copy is dirty!;   \
		echo Commit your changes and try again.;  \
		exit -1;                                  \
	fi;

# System Installation ##########################################################

.PHONY: develop
develop:
	$(SYS_PYTHON) setup.py develop

.PHONY: install
install:
	$(SYS_PYTHON) setup.py install

.PHONY: download
download:
	pip install $(PROJECT)
