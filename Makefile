# local run
run:
	sh -c "source ./env.sh;python src/main.py;"

run-mongo:
	mongod --dbpath ./db --auth

init-mongo:
	python restart-mongod.py

restart-mongo:
	$(MAKE) init-mongo
	$(MAKE) run-mongo

# docker
run-docker:
	sh -c "source ./env.sh;docker-compose up --wait;"

kill-docker:
	docker kill abigail-mongo-1 abigail-python-1

