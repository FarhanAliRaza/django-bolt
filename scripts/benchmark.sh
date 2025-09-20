#!/bin/bash
# Clean benchmark runner for Django-Bolt

P=${P:-2}
WORKERS=${WORKERS:-2}
C=${C:-50}
N=${N:-10000}
HOST=${HOST:-127.0.0.1}
PORT=${PORT:-8000}

echo "# Django-Bolt Benchmark"
echo "Generated: $(date)"
echo "Config: $P processes × $WORKERS workers | C=$C N=$N"
echo ""

echo "## Hello World Performance"
cd python/examples/testproject
DJANGO_BOLT_WORKERS=$WORKERS nohup uv run python manage.py runbolt --host $HOST --port $PORT --processes $P >/dev/null 2>&1 &
SERVER_PID=$!
sleep 2

ab -k -c $C -n $N http://$HOST:$PORT/hello 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"

kill $SERVER_PID 2>/dev/null || true
sleep 1

echo ""
echo "## ORM Performance"
uv run python manage.py makemigrations users --noinput >/dev/null 2>&1 || true
uv run python manage.py migrate --noinput >/dev/null 2>&1 || true

DJANGO_BOLT_WORKERS=$WORKERS nohup uv run python manage.py runbolt --host $HOST --port $PORT --processes $P >/dev/null 2>&1 &
SERVER_PID=$!
sleep 2

curl -s http://$HOST:$PORT/users/seed >/dev/null 2>&1 || true
sleep 1

ab -k -c $C -n $N http://$HOST:$PORT/users/ 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"

kill $SERVER_PID 2>/dev/null || true
