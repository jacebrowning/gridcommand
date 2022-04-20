.phony: install
install:
	poetry install

.phony: run
run: install
	FLASK_DEBUG=1 poetry run flask run
