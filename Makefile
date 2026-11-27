.PHONY: install test lint audit demo serve docker
install:  ## editable install with dev tools
	pip install -e ".[dev]"
test:     ## run the test suite (offline, under a second)
	pytest -q
lint:     ## style + security lint
	ruff check src tests && bandit -q -r src
audit:    ## known-vulnerability scan of dependencies
	pip-audit
demo:     ## talk to Jager offline, no keys
	jager demo
serve:    ## run the webhook server
	jager serve
docker:   ## build and start with Docker
	docker compose up -d --build
