all: test run

run:
	python main.py

test:
	python -m unittest discover tests

clean:
	rm -rf __pycache__

