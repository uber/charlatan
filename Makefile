.PHONY: bootstrap develop

all: bootstrap develop test

bootstrap:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	pip install -r requirements-test.txt

develop:
	python setup.py develop

test: clean develop lint
	python setup.py test

test-all: clean lint
	tox

tu:
	py.test

lint:
	flake8 charlatan

coverage:
	coverage run --source charlatan setup.py test
	coverage report -m
	coverage html
	open htmlcov/index.html

clean: clean-build
	find . -name '*.py[co]' -exec rm -f {} +

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info

release: clean test docs
	fullrelease

doc: clean develop
	$(MAKE) -C docs clean
	$(MAKE) -C docs html

open_doc: doc
	open docs/_build/html/index.html
