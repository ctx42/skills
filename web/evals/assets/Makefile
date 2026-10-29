# Every check: Go vet and tests, then the frontend check.
check:
	go vet ./...
	go test ./...
	cd web && bun run check

# The frontend build the server embeds, then the end-to-end tests.
test: check
	cd web && bun run test

.PHONY: check test
