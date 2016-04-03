
default:
	@echo "make env  - make a virtualenv under ./env"
	@echo "make test - run tests"

env:
	virtualenv env
	./env/bin/python setup.py install

test: env
	./env/bin/python test/runner.py

clean:
	rm -rf env dist *.egg-info
	find . -name \*.pyc | xargs rm 

.PHONY: test default clean

