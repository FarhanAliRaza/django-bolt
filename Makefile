# Common developer commands (uses uv + maturin)

HOST ?= 127.0.0.1
PORT ?= 8000
C ?= 100
N ?= 50000

.PHONY: develop run run-bg kill smoke bench migrate orm-smoke create-user clean reinstall

develop:
	uv run maturin develop

run:
	uv run python python/examples/embedded_app.py

run-bg:
	nohup uv run python python/examples/embedded_app.py > /tmp/django-bolt.log 2>&1 & echo $$! > /tmp/django-bolt.pid && echo "started: $$! (logs: /tmp/django-bolt.log)"

kill:
	@pids=$$(lsof -tiTCP:$(PORT) -sTCP:LISTEN 2>/dev/null || true); \
	if [ -n "$$pids" ]; then \
		echo "killing: $$pids"; kill $$pids 2>/dev/null || true; sleep 0.3; \
		p2=$$(lsof -tiTCP:$(PORT) -sTCP:LISTEN 2>/dev/null || true); \
		[ -n "$$p2" ] && echo "force-killing: $$p2" && kill -9 $$p2 2>/dev/null || true; \
	else \
		echo "no listener on :$(PORT)"; \
	fi

smoke:
	curl -sS http://$(HOST):$(PORT)/hello | cat

bench:
	@if command -v ab >/dev/null 2>&1; then \
		ab -k -c $(C) -n $(N) http://$(HOST):$(PORT)/hello; \
	else \
		echo "ab not found. install apachebench (ab) or adjust this target."; \
	fi

migrate:
	uv run python -c 'from django_bolt.bootstrap import ensure_django_ready; info = ensure_django_ready(); print("migrated: mode={} db={}".format(info.get("mode"), info.get("database_name")))'

makemigrations:
	uv run django-bolt makemigrations

orm-smoke:
	uv run python -c 'from django_bolt.bootstrap import ensure_django_ready; ensure_django_ready(); from django.contrib.auth.models import User; print("users: {}".format(User.objects.count()))'

create-user:
	uv run python -c 'from django_bolt.bootstrap import ensure_django_ready; ensure_django_ready(); from django.contrib.auth.models import User; u, created = User.objects.get_or_create(username="demo", defaults={"is_staff": True, "is_superuser": False}); u.set_password("demo"); u.save(); print("user: {} created={}".format(u.username, created))'

clean:
	cargo clean

reinstall: kill clean develop

