# Django-Bolt Development Commands

HOST ?= 127.0.0.1
PORT ?= 8001
C ?= 100
N ?= 10000
P ?= 10
WORKERS ?= 1

.PHONY: build test-server test-server-bg kill bench clean orm-test setup-test-data seed-data orm-smoke compare-frameworks save-baseline test-py

# Build Rust extension in release mode
build:
	uv run maturin develop --release


# Start test server in background with multi-process
run-bg:
	cd python/examples/testproject && \
	DJANGO_BOLT_WORKERS=$(WORKERS) nohup uv run python manage.py runbolt --host $(HOST) --port $(PORT) --processes $(P) \
		> /tmp/django-bolt-test.log 2>&1 & echo $$! > /tmp/django-bolt-test.pid && \
		echo "started: $$(cat /tmp/django-bolt-test.pid) (log: /tmp/django-bolt-test.log)"

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

# Benchmark root endpoint
bench:
	@echo "Benchmarking http://$(HOST):$(PORT)/ with C=$(C) N=$(N)"
	@echo "Config: $(P) processes, $(WORKERS) workers per process"
	@if command -v ab >/dev/null 2>&1; then \
		ab -k -c $(C) -n $(N) http://$(HOST):$(PORT)/; \
	else \
		echo "ab not found. install apachebench: sudo apt install apache2-utils"; \
	fi

# Quick smoke test
smoke:
	@echo "Testing endpoints..."
	@curl -s http://$(HOST):$(PORT)/ | head -1
	@curl -s http://$(HOST):$(PORT)/items/1 | head -1
	@curl -s http://$(HOST):$(PORT)/users/ | head -1

# ORM smoke test (requires seeded data)
orm-smoke:
	@echo "Testing ORM endpoints..."
	@curl -s http://$(HOST):$(PORT)/users/stats | head -1
	@curl -s http://$(HOST):$(PORT)/users/1 | head -1

# Clean build artifacts
clean:
	cargo clean
	rm -rf target/
	rm -f python/django_bolt/*.so

# Full rebuild
rebuild: kill clean build

# Development workflow: build, start server, run benchmark
dev-test: build test-server-bg
	@sleep 2
	@make smoke
	@make bench
	@make kill

# Run Python tests (verbose)
test-py:
	uv run --with pytest pytest python/django_bolt/tests -s -vv

# High-performance test (for benchmarking)
perf-test: build
	@echo "High-performance test: 4 processes, 1 worker each"
	@make test-server-bg P=4 WORKERS=1
	@sleep 2
	@make bench C=100 N=50000
	@make kill

# ORM performance test
orm-test: build
	@echo "Setting up test data..."
	@cd python/examples/testproject && uv run python manage.py makemigrations users --noinput
	@cd python/examples/testproject && uv run python manage.py migrate --noinput
	@echo "ORM performance test: 2 processes, 2 workers each"
	@make test-server-bg P=2 WORKERS=2
	@sleep 3
	@echo "Seeding database..."
	@curl -s http://$(HOST):$(PORT)/users/seed | head -1
	@sleep 1
	@echo "Benchmarking ORM endpoint /users/ ..."
	@ab -k -c $(C) -n $(N) http://$(HOST):$(PORT)/users/ | grep -E "(Requests per second|Time per request|Failed requests)"
	@make kill

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

