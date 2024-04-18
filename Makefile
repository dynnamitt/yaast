
dist: setup.cfg
	python3 -m build

upload: dist/yaast*.tar.gz
	python3 -m twine upload --repository pypi dist/*

deps:
	python3 -m pip install --upgrade build twine
	
develop:
	python3 -m src.yaast --help
	
clean:
	rm -rf dist/
