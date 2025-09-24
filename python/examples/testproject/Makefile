# Django ASGI/Uvicorn Makefile

# Default values
HOST ?= 0.0.0.0
PORT ?= 8000
WORKERS ?= 4

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[0;33m
NC := \033[0m # No Color

.PHONY: help
help:
	@echo "$(GREEN)Django ASGI Server Commands:$(NC)"
	@echo "  $(YELLOW)make run-asgi$(NC)       - Run with Uvicorn (production mode)"
	@echo "  $(YELLOW)make run-asgi-dev$(NC)   - Run with Uvicorn (development mode with reload)"
	@echo "  $(YELLOW)make run-django$(NC)     - Run with Django dev server"
	@echo "  $(YELLOW)make test-plain$(NC)     - Test plain Django endpoints"
	@echo ""
	@echo "$(GREEN)Options:$(NC)"
	@echo "  HOST=$(HOST) PORT=$(PORT) WORKERS=$(WORKERS)"
	@echo ""
	@echo "$(GREEN)Examples:$(NC)"
	@echo "  make run-asgi HOST=127.0.0.1 PORT=8080 WORKERS=8"
	@echo "  make run-asgi-dev"

.PHONY: run-asgi
run-asgi:
	@echo "$(GREEN)Starting Django with Uvicorn ASGI server...$(NC)"
	@echo "Host: $(HOST):$(PORT), Workers: $(WORKERS)"
	@uvicorn testproject.asgi:application \
		--host $(HOST) \
		--port $(PORT) \
		--workers $(WORKERS) \
		--loop uvloop \
		--http httptools \
		--log-level error

.PHONY: run-asgi-dev
run-asgi-dev:
	@echo "$(GREEN)Starting Django with Uvicorn ASGI server (dev mode)...$(NC)"
	@echo "Host: $(HOST):$(PORT), Reload: enabled"
	@uvicorn testproject.asgi:application \
		--host $(HOST) \
		--port $(PORT) \
		--reload \
		--log-level debug

.PHONY: run-django
run-django:
	@echo "$(GREEN)Starting Django development server...$(NC)"
	@python manage.py runserver $(HOST):$(PORT)

.PHONY: test-plain
test-plain:
	@echo "$(GREEN)Testing Django plain endpoints...$(NC)"
	@echo "$(YELLOW)Testing root endpoint:$(NC)"
	@curl -s http://$(HOST):$(PORT)/plain/ | python -m json.tool
	@echo ""
	@echo "$(YELLOW)Testing items endpoint:$(NC)"
	@curl -s "http://$(HOST):$(PORT)/plain/items/42?q=test" | python -m json.tool
	@echo ""
	@echo "$(YELLOW)Testing users endpoint:$(NC)"
	@curl -s http://$(HOST):$(PORT)/plain/users/ | python -m json.tool
	@echo ""
	@echo "$(YELLOW)Testing POST endpoint:$(NC)"
	@curl -s -X POST http://$(HOST):$(PORT)/plain/bench/parse \
		-H "Content-Type: application/json" \
		-d '{"title": "test", "count": 5, "items": [{"name": "item1", "price": 10.0}]}' | python -m json.tool

.PHONY: benchmark-plain
benchmark-plain:
	@echo "$(GREEN)Benchmarking Django plain endpoints...$(NC)"
	@echo "$(YELLOW)Benchmarking root endpoint (10k requests):$(NC)"
	@ab -n 10000 -c 100 http://$(HOST):$(PORT)/plain/
	@echo ""
	@echo "$(YELLOW)Benchmarking items100 endpoint (1k requests):$(NC)"
	@ab -n 1000 -c 50 http://$(HOST):$(PORT)/plain/items100

.PHONY: install-deps
install-deps:
	@echo "$(GREEN)Installing dependencies...$(NC)"
	@pip install uvicorn[standard] uvloop httptools

.PHONY: migrate
migrate:
	@echo "$(GREEN)Running Django migrations...$(NC)"
	@python manage.py migrate

.PHONY: shell
shell:
	@python manage.py shell

.PHONY: clean
clean:
	@echo "$(GREEN)Cleaning up...$(NC)"
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -delete
	@find . -type f -name ".DS_Store" -delete
