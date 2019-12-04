.PHONY: lint test

lint:
	pipenv run pylint *.py

test:
	pipenv run python -m unittest discover
