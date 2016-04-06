
default:
	@echo "make env  - make a virtualenv under ./env"
	@echo "make test - run tests"

env:
	virtualenv env
	./env/bin/python setup.py install

package:
	python setup.py bdist_wheel

test: env
	./env/bin/python test/runner.py

clean:
	rm -rf env dist *.egg-info
	find . -name \*.pyc | xargs rm 

.PHONY: default package test clean

