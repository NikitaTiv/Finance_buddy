style:
	flake8 .

types:
	mypy .

check:
	make style types
