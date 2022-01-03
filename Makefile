OUTDATED_IMG := $(shell docker images | grep none | wc -l)

all: test run

run:
	python main.py

test:
	python -m pytest -v tests
	python -m pytest --cov=. tests

clean:
ifneq ($(OUTDATED_IMG), 0)
	docker rmi `docker images | grep none |awk '{print $$3}'`
endif
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete
