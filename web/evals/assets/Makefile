PORT ?= 8138

serve:
	PORT=$(PORT) python3 server.py

check:
	./check.sh

bench:
	for f in tests/*.bench.js; do node "$$f"; done

.PHONY: serve check bench
