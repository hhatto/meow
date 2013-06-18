all:
	@echo "make pypireg"
	@echo "make clean"

clean:
	rm -rf .tmp.test.py temp *.pyc *egg-info dist build \
		__pycache__ */__pycache__ */*/__pycache__ \
		htmlcov coverage.xml

pypireg:
	${PYTHON} setup.py register
	${PYTHON} setup.py sdist upload
