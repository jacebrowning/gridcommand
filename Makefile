.PHONY: install
install:
	poetry install

.PHONY: run
run: install
	FLASK_DEBUG=1 poetry run flask run

.PHONY: serve
serve:
	git pull
	make install
	status=1; while [ $$status -eq 1 ]; do poetry run flask run; status=$$?; sleep 1; done
