.PHONY: run test

run:
	poetry run flask --app user_monitoring.main:app run --debug

test:
	poetry run python -m pytest -vvv
