# Django-Bolt Development Commands

HOST ?= 127.0.0.1
PORT ?= 8001
C ?= 100
N ?= 10000
P ?= 8
WORKERS ?= 1

.PHONY: build test-server test-server-bg kill bench clean orm-test setup-test-data seed-data orm-smoke compare-frameworks save-baseline test-py

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


# Seed database with test data
seed-data:
	@echo "Seeding database..."
	@curl -s http://$(HOST):$(PORT)/users/seed | head -1


# Save baseline vs dev benchmark comparison
save-bench:
	@if [ ! -f BENCHMARK_BASELINE.md ]; then \
		echo "Creating baseline benchmark..."; \
		P=$(P) WORKERS=$(WORKERS) C=$(C) N=$(N) HOST=$(HOST) PORT=$(PORT) ./scripts/benchmark.sh > BENCHMARK_BASELINE.md; \
		echo "✅ Baseline saved to BENCHMARK_BASELINE.md"; \
	elif [ ! -f BENCHMARK_DEV.md ]; then \
		echo "Creating dev benchmark..."; \
		P=$(P) WORKERS=$(WORKERS) C=$(C) N=$(N) HOST=$(HOST) PORT=$(PORT) ./scripts/benchmark.sh > BENCHMARK_DEV.md; \
		echo "✅ Dev version saved to BENCHMARK_DEV.md"; \
		echo ""; \
		echo "=== PERFORMANCE COMPARISON ==="; \
		echo "Baseline:"; \
		grep "Requests per second" BENCHMARK_BASELINE.md | head -2; \
		echo "Dev:"; \
		grep "Requests per second" BENCHMARK_DEV.md | head -2; \
		echo ""; \
		echo "Streaming (Plain) RPS - Dev:"; \
		awk '/### Streaming Plain/{flag=1;next} /###/{flag=0} flag && /Requests per second/{print}' BENCHMARK_DEV.md || true; \
		echo "Streaming (SSE) RPS - Dev:"; \
		awk '/### Server-Sent Events/{flag=1;next} /###/{flag=0} flag && /Requests per second/{print}' BENCHMARK_DEV.md || true; \
	else \
		echo "Rotating benchmarks: dev -> baseline, new -> dev"; \
		mv BENCHMARK_DEV.md BENCHMARK_BASELINE.md; \
		P=$(P) WORKERS=$(WORKERS) C=$(C) N=$(N) HOST=$(HOST) PORT=$(PORT) ./scripts/benchmark.sh > BENCHMARK_DEV.md; \
		echo "✅ New dev version saved, old dev moved to baseline"; \
		echo ""; \
		echo "=== PERFORMANCE COMPARISON ==="; \
		echo "Baseline (old dev):"; \
		grep "Requests per second" BENCHMARK_BASELINE.md | head -2; \
		echo "Dev (current):"; \
		grep "Requests per second" BENCHMARK_DEV.md | head -2; \
		echo ""; \
		echo "Streaming (Plain) RPS - Baseline:"; \
		awk '/### Streaming Plain/{flag=1;next} /###/{flag=0} flag && /Requests per second/{print}' BENCHMARK_BASELINE.md || true; \
		echo "Streaming (SSE) RPS - Baseline:"; \
		awk '/### Server-Sent Events/{flag=1;next} /###/{flag=0} flag && /Requests per second/{print}' BENCHMARK_BASELINE.md || true; \
		echo "Streaming (Plain) RPS - Dev:"; \
		awk '/### Streaming Plain/{flag=1;next} /###/{flag=0} flag && /Requests per second/{print}' BENCHMARK_DEV.md || true; \
		echo "Streaming (SSE) RPS - Dev:"; \
		awk '/### Server-Sent Events/{flag=1;next} /###/{flag=0} flag && /Requests per second/{print}' BENCHMARK_DEV.md || true; \
	fi



build-bench:
	uv run maturin develop --release
	make save-bench
