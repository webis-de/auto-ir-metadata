build-pypi-package: run-tests
	rm -Rf dist
	python3 -m build --sdist .
	python3 -m build --wheel .
	twine upload dist/auto_ir_metadata-*.whl dist/auto_ir_metadata-*.tar.gz

run-tests:
	PYTHONPATH=. pytest

