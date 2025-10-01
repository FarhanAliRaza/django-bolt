#!/bin/bash
# Clean benchmark runner for Django-Bolt

P=${P:-2}
WORKERS=${WORKERS:-2}
C=${C:-100}
N=${N:-10000}
HOST=${HOST:-127.0.0.1}
PORT=${PORT:-8000}
# Timeout in seconds for streaming load tests
HEY_TIMEOUT=${HEY_TIMEOUT:-60}
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
# DJANGO_BOLT_WORKERS=$WORKERS setsid uv run python manage.py runbolt --host $HOST --port $PORT --processes $P >/dev/null 2>&1 &
# SERVER_PID=$!
sleep 2

# Sanity check: ensure 200 OK before benchmarking
CODE=$(curl -s -o /dev/null -w '%{http_code}' http://$HOST:$PORT/)
if [ "$CODE" != "200" ]; then
  echo "Expected 200 from / but got $CODE; aborting benchmark." >&2
  kill -TERM -$SERVER_PID 2>/dev/null || true
  pkill -TERM -f "manage.py runbolt --host $HOST --port $PORT" 2>/dev/null || true
  exit 1
fi 

ab -k -c $C -n $N http://$HOST:$PORT/ 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"

echo ""
echo "## Response Type Endpoints"

printf "\n### Header Endpoint (/header)\n"
ab -k -c $C -n $N -H 'x-test: val' http://$HOST:$PORT/header 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"

printf "\n### Cookie Endpoint (/cookie)\n"
ab -k -c $C -n $N -H 'Cookie: session=abc' http://$HOST:$PORT/cookie 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"

printf "\n### Exception Endpoint (/exc)\n"
ab -k -c $C -n $N http://$HOST:$PORT/exc 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"

printf "\n### HTML Response (/html)\n"
ab -k -c $C -n $N http://$HOST:$PORT/html 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"

printf "\n### Redirect Response (/redirect)\n"
ab -k -c $C -n $N -r -H 'Accept: */*' http://$HOST:$PORT/redirect 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"

printf "\n### File Static via FileResponse (/file-static)\n"
ab -k -c $C -n $N http://$HOST:$PORT/file-static 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"

# Streaming and SSE tests using hey (better than ab for streaming)
echo ""
echo "## Streaming and SSE Performance"

# Check if hey is available
HEY_BIN=""
if command -v hey &> /dev/null; then
    HEY_BIN="hey"
elif [ -f "$HOME/go/bin/hey" ]; then
    HEY_BIN="$HOME/go/bin/hey"
elif [ -f "$HOME/.local/bin/hey" ]; then
    HEY_BIN="$HOME/.local/bin/hey"
fi

if [ -n "$HEY_BIN" ]; then
    printf "\n### Streaming Plain Text (/stream)\n"
    timeout "$HEY_TIMEOUT" $HEY_BIN -n $N -c $C http://$HOST:$PORT/stream 2>&1 | grep -E "(Requests/sec:|Total:|Fastest:|Slowest:|Average:|Status code distribution:)" | head -10 || echo "(stream timed out after ${HEY_TIMEOUT}s)"
    
    printf "\n### Server-Sent Events (/sse)\n"
    timeout "$HEY_TIMEOUT" $HEY_BIN -n $N -c $C -H "Accept: text/event-stream" http://$HOST:$PORT/sse 2>&1 | grep -E "(Requests/sec:|Total:|Fastest:|Slowest:|Average:|Status code distribution:)" | head -10 || echo "(sse timed out after ${HEY_TIMEOUT}s)"

    printf "\n### Server-Sent Events (async) (/sse-async)\n"
    timeout "$HEY_TIMEOUT" $HEY_BIN -n $N -c $C -H "Accept: text/event-stream" http://$HOST:$PORT/sse-async 2>&1 | grep -E "(Requests/sec:|Total:|Fastest:|Slowest:|Average:|Status code distribution:)" | head -10 || echo "(sse-async timed out after ${HEY_TIMEOUT}s)"

    printf "\n### OpenAI Chat Completions (stream) (/v1/chat/completions)\n"
    BODY_STREAM='{"model":"gpt-4o-mini","messages":[{"role":"user","content":"Say hi"}],"stream":true,"n_chunks":50,"token":" hi","delay_ms":0}'
    echo "$BODY_STREAM" > /tmp/bolt_chat_stream.json
    timeout "$HEY_TIMEOUT" $HEY_BIN -n $N -c $C -H "Content-Type: application/json" -m POST -D /tmp/bolt_chat_stream.json http://$HOST:$PORT/v1/chat/completions 2>&1 | grep -E "(Requests/sec:|Total:|Fastest:|Slowest:|Average:|Bytes In|Bytes Out|Status code distribution:)" | head -15 || echo "(chat stream timed out after ${HEY_TIMEOUT}s)"

    printf "\n### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)\n"
    BODY_STREAM_ASYNC='{"model":"gpt-4o-mini","messages":[{"role":"user","content":"Say hi"}],"stream":true,"n_chunks":50,"token":" hi","delay_ms":0}'
    echo "$BODY_STREAM_ASYNC" > /tmp/bolt_chat_stream_async.json
    timeout "$HEY_TIMEOUT" $HEY_BIN -n $N -c $C -H "Content-Type: application/json" -m POST -D /tmp/bolt_chat_stream_async.json http://$HOST:$PORT/v1/chat/completions-async 2>&1 | grep -E "(Requests/sec:|Total:|Fastest:|Slowest:|Average:|Bytes In|Bytes Out|Status code distribution:)" | head -15 || echo "(chat async stream timed out after ${HEY_TIMEOUT}s)"
else
    echo "hey not installed. Run: ./scripts/install_hey.sh"
fi

# Additional endpoint: GET /items/{item_id}
echo ""
echo "## Items GET Performance (/items/1?q=hello)"
ab -k -c $C -n $N "http://$HOST:$PORT/items/1?q=hello" 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"

# Additional endpoint: PUT /items/{item_id} with JSON body
echo ""
echo "## Items PUT JSON Performance (/items/1)"
BODY_FILE=$(mktemp)
echo '{"name":"bench","price":1.23,"is_offer":true}' > "$BODY_FILE"

# Sanity check: ensure PUT returns 200 OK before benchmarking
PCODE=$(curl -s -o /dev/null -w '%{http_code}' -X PUT -H 'Content-Type: application/json' --data-binary @"$BODY_FILE" http://$HOST:$PORT/items/1)
if [ "$PCODE" != "200" ]; then
  echo "Expected 200 from PUT /items/1 but got $PCODE; skipping Items PUT benchmark." >&2
else
  # Use -u for PUT body with ab
  ab -k -c $C -n $N -u "$BODY_FILE" -T 'application/json' http://$HOST:$PORT/items/1 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests|Non-2xx responses)"
fi
rm -f "$BODY_FILE"

kill -TERM -$SERVER_PID 2>/dev/null || true
pkill -TERM -f "manage.py runbolt --host $HOST --port $PORT" 2>/dev/null || true
sleep 1

echo ""
echo "## ORM Performance"
uv run python manage.py makemigrations users --noinput >/dev/null 2>&1 || true
uv run python manage.py migrate --noinput >/dev/null 2>&1 || true

# DJANGO_BOLT_WORKERS=$WORKERS setsid uv run python manage.py runbolt --host $HOST --port $PORT --processes $P >/dev/null 2>&1 &
SERVER_PID=$!
sleep 2

# Sanity check
UCODE=$(curl -s -o /dev/null -w '%{http_code}' http://$HOST:$PORT/users/full10)
if [ "$UCODE" != "200" ]; then
  echo "Expected 200 from /users/full10 but got $UCODE; aborting ORM benchmark." >&2
  kill $SERVER_PID 2>/dev/null || true
  exit 1
fi

echo "### Users Full10 (/users/full10)"
ab -k -c $C -n $N http://$HOST:$PORT/users/full10 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"

echo "\n### Users Mini10 (/users/mini10)"
ab -k -c $C -n $N http://$HOST:$PORT/users/mini10 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"

kill -TERM -$SERVER_PID 2>/dev/null || true
pkill -TERM -f "manage.py runbolt --host $HOST --port $PORT" 2>/dev/null || true

echo ""
echo "## Form and File Upload Performance"

# Start server for form/file tests
# DJANGO_BOLT_WORKERS=$WORKERS setsid uv run python manage.py runbolt --host $HOST --port $PORT --processes $P >/dev/null 2>&1 &
SERVER_PID=$!
sleep 2

echo "\n### Form Data (POST /form)"
# Create form data
FORM_FILE=$(mktemp)
echo "name=TestUser&age=25&email=test%40example.com" > "$FORM_FILE"
ab -k -c $C -n $N -p "$FORM_FILE" -T 'application/x-www-form-urlencoded' http://$HOST:$PORT/form 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"
rm -f "$FORM_FILE"

echo "\n### File Upload (POST /upload)"
# Create a multipart form data file
UPLOAD_FILE=$(mktemp)
BOUNDARY="----BoltBenchmark$(date +%s)"
cat > "$UPLOAD_FILE" << EOF
--$BOUNDARY
Content-Disposition: form-data; name="file"; filename="test1.txt"
Content-Type: text/plain

This is test file content 1
--$BOUNDARY
Content-Disposition: form-data; name="file"; filename="test2.txt"
Content-Type: text/plain

This is test file content 2
--$BOUNDARY--
EOF
ab -k -c $C -n $N -p "$UPLOAD_FILE" -T "multipart/form-data; boundary=$BOUNDARY" http://$HOST:$PORT/upload 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"
rm -f "$UPLOAD_FILE"

# Mixed form with files benchmark
echo "\n### Mixed Form with Files (POST /mixed-form)"
MIXED_FILE=$(mktemp)
BOUNDARY="----BoltMixed$(date +%s)"
cat > "$MIXED_FILE" << EOF
--$BOUNDARY
Content-Disposition: form-data; name="title"

Test Title
--$BOUNDARY
Content-Disposition: form-data; name="description"

This is a test description
--$BOUNDARY
Content-Disposition: form-data; name="file"; filename="attachment.txt"
Content-Type: text/plain

File attachment content
--$BOUNDARY--
EOF
ab -k -c $C -n $N -p "$MIXED_FILE" -T "multipart/form-data; boundary=$BOUNDARY" http://$HOST:$PORT/mixed-form 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"
rm -f "$MIXED_FILE"

kill -TERM -$SERVER_PID 2>/dev/null || true
pkill -TERM -f "manage.py runbolt --host $HOST --port $PORT" 2>/dev/null || true

echo ""
echo "## Django Ninja-style Benchmarks"

# JSON Parsing/Validation

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

echo "### JSON Parse/Validate (POST /bench/parse)"
# Start a fresh server for this test
# DJANGO_BOLT_WORKERS=$WORKERS setsid uv run python manage.py runbolt --host $HOST --port $PORT --processes $P >/dev/null 2>&1 &
SERVER_PID=$!
sleep 2

# Sanity check
PCODE=$(curl -s -o /dev/null -w '%{http_code}' http://$HOST:$PORT/)
if [ "$PCODE" != "200" ]; then
  echo "Expected 200 from / before parse test but got $PCODE; skipping." >&2
else
  ab -k -c $C -n $N -p "$BODY_FILE" -T 'application/json' http://$HOST:$PORT/bench/parse 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"
fi
kill -TERM -$SERVER_PID 2>/dev/null || true
pkill -TERM -f "manage.py runbolt --host $HOST --port $PORT" 2>/dev/null || true
rm -f "$BODY_FILE"


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
