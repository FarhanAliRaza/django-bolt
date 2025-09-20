#!/bin/bash
# Clean benchmark runner for Django-Bolt

P=${P:-2}
WORKERS=${WORKERS:-2}
C=${C:-50}
N=${N:-10000}
HOST=${HOST:-127.0.0.1}
PORT=${PORT:-8000}
# Slow-op benchmark knobs
SLOW_MS=${SLOW_MS:-100}
SLOW_CONC=${SLOW_CONC:-50}
SLOW_DURATION=${SLOW_DURATION:-5}
WORKER_SET=${WORKER_SET:-"1 2 4 8 12 16 24"}

echo "# Django-Bolt Benchmark"
echo "Generated: $(date)"
echo "Config: $P processes × $WORKERS workers | C=$C N=$N"
echo ""

echo "## Root Endpoint Performance"
cd python/examples/testproject
DJANGO_BOLT_WORKERS=$WORKERS nohup uv run python manage.py runbolt --host $HOST --port $PORT --processes $P >/dev/null 2>&1 &
SERVER_PID=$!
sleep 2

# Sanity check: ensure 200 OK before benchmarking
CODE=$(curl -s -o /dev/null -w '%{http_code}' http://$HOST:$PORT/)
if [ "$CODE" != "200" ]; then
  echo "Expected 200 from / but got $CODE; aborting benchmark." >&2
  kill $SERVER_PID 2>/dev/null || true
  exit 1
fi

ab -k -c $C -n $N http://$HOST:$PORT/ 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"

# Additional endpoint: GET /items/{item_id}
echo ""
echo "## Items GET Performance (/items/1?q=hello)"
ab -k -c $C -n $N "http://$HOST:$PORT/items/1?q=hello" 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"

# Additional endpoint: PUT /items/{item_id} with JSON body
echo ""
echo "## Items PUT JSON Performance (/items/1)"
BODY_FILE=$(mktemp)
echo '{"name":"bench","price":1.23,"is_offer":true}' > "$BODY_FILE"
ab -k -c $C -n $N -T 'application/json' -u "$BODY_FILE" http://$HOST:$PORT/items/1 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"
rm -f "$BODY_FILE"

kill $SERVER_PID 2>/dev/null || true
sleep 1

echo ""
echo "## ORM Performance"
uv run python manage.py makemigrations users --noinput >/dev/null 2>&1 || true
uv run python manage.py migrate --noinput >/dev/null 2>&1 || true

DJANGO_BOLT_WORKERS=$WORKERS nohup uv run python manage.py runbolt --host $HOST --port $PORT --processes $P >/dev/null 2>&1 &
SERVER_PID=$!
sleep 2

# Sanity check
UCODE=$(curl -s -o /dev/null -w '%{http_code}' http://$HOST:$PORT/users/full10)
if [ "$UCODE" != "200" ]; then
  echo "Expected 200 from /users/full10 but got $UCODE; aborting ORM benchmark." >&2
  kill $SERVER_PID 2>/dev/null || true
  exit 1
fi

echo "\n### Users Full10 (/users/full10)"
ab -k -c $C -n $N http://$HOST:$PORT/users/full10 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"

echo "\n### Users Mini10 (/users/mini10)"
ab -k -c $C -n $N http://$HOST:$PORT/users/mini10 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"

kill $SERVER_PID 2>/dev/null || true

echo ""
echo "## Django Ninja-style Benchmarks"

# JSON Parsing/Validation at concurrency=1 via POST /bench/parse
DJANGO_BOLT_WORKERS=$WORKERS nohup uv run python manage.py runbolt --host $HOST --port $PORT --processes $P >/dev/null 2>&1 &
SERVER_PID=$!
sleep 2

BODY_FILE=$(mktemp)
cat > "$BODY_FILE" << 'JSON'
{
  "title": "bench",
  "count": 100,
  "items": [
    {"name": "a", "price": 1.0, "is_offer": true}
  ]
}
JSON

echo "\n### JSON Parse/Validate (c=1, POST /bench/parse)"
ab -q -c 1 -n $N -T 'application/json' -u "$BODY_FILE" http://$HOST:$PORT/bench/parse 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"
rm -f "$BODY_FILE"

kill $SERVER_PID 2>/dev/null || true
sleep 1

# echo "\n### Slow Async Operation (GET /bench/slow?ms=$SLOW_MS, c=$SLOW_CONC, t=${SLOW_DURATION}s)"
# for W in $WORKER_SET; do
#   DJANGO_BOLT_WORKERS=$W nohup uv run python manage.py runbolt --host $HOST --port $PORT --processes $P >/dev/null 2>&1 &
#   SERVER_PID=$!
#   # Wait up to 3s for readiness
#   for i in $(seq 1 30); do
#     CODE=$(curl -s -o /dev/null -w '%{http_code}' "http://$HOST:$PORT/bench/slow?ms=$SLOW_MS")
#     [ "$CODE" = "200" ] && break
#     sleep 0.1
#   done
#   RPS=$(ab -q -s 5 -k -c $SLOW_CONC -t $SLOW_DURATION "http://$HOST:$PORT/bench/slow?ms=$SLOW_MS" 2>/dev/null | grep "Requests per second" | awk '{print $4}')
#   echo "workers=$W: ${RPS:-0} rps"
#   kill $SERVER_PID 2>/dev/null || true
#   sleep 0.3
# done
