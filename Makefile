
PYTHON=python

default:
	@echo "make env  - make a virtualenv under ./env"
	@echo "make test - run tests"

env:
	virtualenv --python=$(PYTHON) env
	./env/bin/pip install -e .[tests]

package:
	python setup.py bdist_wheel

oldtest:
	./env/bin/python test/runner.py

test: env
	./env/bin/py.test test/

test1: env
	./env/bin/py.test -x -ff --timeout=30 test/

clean:
	rm -rf env build dist *.egg *.egg-info
	find . -name \*.pyc | xargs rm -f

.PHONY: default package test clean

