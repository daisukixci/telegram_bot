OUTDATED_IMG := $(shell sudo docker images | grep none | wc -l)

all: test run

run:
	python main.py

test:
	poetry run pytest -v tests
	poetry run pytest --cov=. tests

clean:
ifneq ($(OUTDATED_IMG), 0)
	sudo docker rmi `sudo docker images | grep none |awk '{print $$3}'`
endif
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete
