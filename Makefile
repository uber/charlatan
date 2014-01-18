all: bootstrap develop test

bootstrap:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	pip install -r requirements-test.txt

develop:
	python setup.py develop

test: clean lint
	python setup.py test

tu:
	py.test

lint:
	flake8 charlatan --ignore=E501,E702

coverage:
	coverage run --source charlatan setup.py test
	coverage report -m
	coverage html
	open htmlcov/index.html

clean:
	find . -name '*.py[co]' -exec rm -f {} +

release: clean test docs
	prerelease && release
	git push --tags
	git push

doc: clean develop
	$(MAKE) -C docs clean
	$(MAKE) -C docs html

open_doc: doc
	open docs/_build/html/index.html
