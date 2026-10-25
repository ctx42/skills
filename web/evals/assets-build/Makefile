PORT ?= 8138

serve:
	PORT=$(PORT) python3 server.py

check:
	./check.sh

bench:
	for f in tests/*.bench.js; do node "$$f"; done

build:
	python3 build.py

.PHONY: serve check bench build
