install:
	pip install -r requirements.txt

build:
	docker build -t abigail .

run:
	docker run -di abigail

enter-sh:
	python scripts/enter-sh.py

kill-all:
	python scripts/kill-all.py