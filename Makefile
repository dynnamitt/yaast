
dist: setup.cfg
	python3 -m pip install --upgrade build
	python3 -m build

upload: dist/yaast*.tar.gz
	python3 -m twine upload --repository pypi dist/*

clean:
	rm -rf dist/
