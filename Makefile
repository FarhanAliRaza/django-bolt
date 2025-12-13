# Django-Bolt Development Commands

HOST ?= 127.0.0.1
PORT ?= 8001
C ?= 100
N ?= 10000
P ?= 8
WORKERS ?= 1

.PHONY: build test-server test-server-bg kill bench clean orm-test setup-test-data seed-data orm-smoke compare-frameworks save-baseline test-py lint lint-lib ruff ruff-fix format release delete-tag

# Build Rust extension in release mode
build:
	uv run maturin develop --release

# Kill any servers on PORT
kill:
	@pids=$$(lsof -tiTCP:$(PORT) -sTCP:LISTEN 2>/dev/null || true); \
	if [ -n "$$pids" ]; then \
		echo "killing: $$pids"; kill $$pids 2>/dev/null || true; sleep 0.3; \
		p2=$$(lsof -tiTCP:$(PORT) -sTCP:LISTEN 2>/dev/null || true); \
		[ -n "$$p2" ] && echo "force-killing: $$p2" && kill -9 $$p2 2>/dev/null || true; \
	fi
	@[ -f /tmp/django-bolt-test.pid ] && kill $$(cat /tmp/django-bolt-test.pid) 2>/dev/null || true
	@rm -f /tmp/django-bolt-test.pid /tmp/django-bolt-test.log


# Clean build artifacts
clean:
	cargo clean
	rm -rf target/
	rm -f python/django_bolt/*.so

# Full rebuild
rebuild: kill clean build



run-dev:
	uv run python python/example/manage.py runbolt --dev
# Run Python tests (verbose)
test-py:
	uv run --with pytest pytest python/tests -s -vv

#   uv run --with pytest pytest python/tests/test_request_user.py -s -vv

# Run ruff linter (checks library code - some S110 errors in tests/examples are expected)
lint:
	uv run ruff check .

# Alias for lint
ruff: lint

# Check only library code (excludes tests and examples)
lint-lib:
	uv run ruff check python/django_bolt

lint-lib-fix:
	uv run ruff check python/django_bolt --fix


# Fix ruff errors automatically
ruff-fix:
	uv run ruff check . --fix

lint-lib-fix:
	uv run ruff check python/django_bolt --fix

lint-lib-fix-unsafe:
	uv run ruff check python/django_bolt --unsafe-fixes --fix

# Format code with ruff
format:
	uv run ruff format .
# Seed database with test data
seed-data:
	@echo "Seeding database..."
	@curl -s http://$(HOST):$(PORT)/users/seed | head -1


# Save baseline vs dev benchmark comparison
save-bench:
	@mkdir -p bench
	@if [ ! -f bench/BENCHMARK_BASELINE.md ]; then \
		echo "Creating baseline benchmark..."; \
		P=$(P) WORKERS=$(WORKERS) C=$(C) N=$(N) HOST=$(HOST) PORT=$(PORT) ./scripts/benchmark.sh > bench/BENCHMARK_BASELINE.md; \
		echo "✅ Baseline saved to bench/BENCHMARK_BASELINE.md"; \
	elif [ ! -f bench/BENCHMARK_DEV.md ]; then \
		echo "Creating dev benchmark..."; \
		P=$(P) WORKERS=$(WORKERS) C=$(C) N=$(N) HOST=$(HOST) PORT=$(PORT) ./scripts/benchmark.sh > bench/BENCHMARK_DEV.md; \
		echo "✅ Dev version saved to bench/BENCHMARK_DEV.md"; \
		echo ""; \
		echo "=== PERFORMANCE COMPARISON ==="; \
		echo "Baseline:"; \
		grep "Requests per second" bench/BENCHMARK_BASELINE.md | head -2; \
		echo "Dev:"; \
		grep "Requests per second" bench/BENCHMARK_DEV.md | head -2; \
		echo ""; \
		echo "Streaming (Plain) RPS - Dev:"; \
		awk '/### Streaming Plain/{flag=1;next} /###/{flag=0} flag && /Requests per second/{print}' bench/BENCHMARK_DEV.md || true; \
		echo "Streaming (SSE) RPS - Dev:"; \
		awk '/### Server-Sent Events/{flag=1;next} /###/{flag=0} flag && /Requests per second/{print}' bench/BENCHMARK_DEV.md || true; \
	else \
		echo "Rotating benchmarks: dev -> baseline, new -> dev"; \
		mv bench/BENCHMARK_DEV.md bench/BENCHMARK_BASELINE.md; \
		P=$(P) WORKERS=$(WORKERS) C=$(C) N=$(N) HOST=$(HOST) PORT=$(PORT) ./scripts/benchmark.sh > bench/BENCHMARK_DEV.md; \
		echo "✅ New dev version saved, old dev moved to baseline"; \
		echo ""; \
		echo "=== PERFORMANCE COMPARISON ==="; \
		echo "Baseline (old dev):"; \
		grep "Requests per second" bench/BENCHMARK_BASELINE.md | head -2; \
		echo "Dev (current):"; \
		grep "Requests per second" bench/BENCHMARK_DEV.md | head -2; \
		echo ""; \
		echo "Streaming (Plain) RPS - Baseline:"; \
		awk '/### Streaming Plain/{flag=1;next} /###/{flag=0} flag && /Requests per second/{print}' bench/BENCHMARK_BASELINE.md || true; \
		echo "Streaming (SSE) RPS - Baseline:"; \
		awk '/### Server-Sent Events/{flag=1;next} /###/{flag=0} flag && /Requests per second/{print}' bench/BENCHMARK_BASELINE.md || true; \
		echo "Streaming (Plain) RPS - Dev:"; \
		awk '/### Streaming Plain/{flag=1;next} /###/{flag=0} flag && /Requests per second/{print}' bench/BENCHMARK_DEV.md || true; \
		echo "Streaming (SSE) RPS - Dev:"; \
		awk '/### Server-Sent Events/{flag=1;next} /###/{flag=0} flag && /Requests per second/{print}' bench/BENCHMARK_DEV.md || true; \
	fi



build-bench:
	uv run maturin develop --release
	make save-bench

# Release new version
# Usage: make release VERSION=0.2.2
# Usage: make release VERSION=0.3.0-alpha1 (for pre-releases)
# Usage: make release VERSION=0.2.2 DRY_RUN=1 (for testing)
release:
	@if [ -z "$(VERSION)" ]; then \
		echo "Error: VERSION is required"; \
		echo "Usage: make release VERSION=0.2.2"; \
		echo "       make release VERSION=0.3.0-alpha1"; \
		echo "       make release VERSION=0.2.2 DRY_RUN=1"; \
		exit 1; \
	fi
	@if [ "$(DRY_RUN)" = "1" ]; then \
		./scripts/release.sh $(VERSION) --dry-run; \
	else \
		./scripts/release.sh $(VERSION); \
	fi

# Delete git tag locally and remotely
# Usage: make delete-tag TAG=v0.2.2
delete-tag:
	@if [ -z "$(TAG)" ]; then \
		echo "Error: TAG is required"; \
		echo "Usage: make delete-tag TAG=v0.2.2"; \
		exit 1; \
	fi
	@echo "Deleting tag $(TAG) locally..."
	@git tag -d $(TAG) || echo "Tag $(TAG) not found locally"
	@echo "Deleting tag $(TAG) from remote..."
	@git push origin :refs/tags/$(TAG) || echo "Tag $(TAG) not found on remote"
	@echo "✅ Tag $(TAG) deleted successfully"
