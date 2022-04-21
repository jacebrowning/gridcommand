FLASK_ENV ?= development

.PHONY: install
install:
	poetry install

.PHONY: run
run: install
	FLASK_ENV=$(FLASK_ENV) poetry run flask run

.PHONY: serve
serve:
	status=1; \
	while [ $$status -eq 1 ] ; do \
		git pull; \
		make run FLASK_ENV=production; \
		status=$$?; \
		sleep 1; \
	done; \
