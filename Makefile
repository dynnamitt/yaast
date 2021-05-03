
build: setup.cfg
	python3 -m build

upload: dist/yaast*.tar.gz
	python3 -m twine upload --repository pypi dist/*
