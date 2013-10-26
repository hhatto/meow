all:
	@echo "make pypireg"
	@echo "make clean"

clean:
	rm -f meow/*.pyc
	rm -rf .tmp.test.py temp *.pyc *egg-info dist build \
		setup.cfg __pycache__ */__pycache__ */*/__pycache__ \
		htmlcov coverage.xml

pypireg:
	python setup.py register
	python setup.py sdist upload
