#!/bin/bash
# Clean benchmark runner for Django-Bolt

P=${P:-2}
WORKERS=${WORKERS:-2}
C=${C:-50}
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
# Mode: bolt (default), django (for uvicorn ASGI), or fastapi
MODE=${MODE:-bolt}
# FastAPI workers (uvicorn processes)
FASTAPI_WORKERS=${FASTAPI_WORKERS:-4}

echo "# Django-Bolt  Benchmark"
echo "Generated: $(date)"
if [ "$MODE" = "fastapi" ]; then
  echo "Config: FastAPI with $FASTAPI_WORKERS uvicorn workers | C=$C N=$N | Mode=$MODE"
else
  echo "Config: $P processes × $WORKERS workers | C=$C N=$N | Mode=$MODE"
fi
echo ""

echo "## Root Endpoint Performance"
cd python/examples/testproject

# Start server based on mode
if [ "$MODE" = "fastapi" ]; then
  # FastAPI with uvicorn workers
  echo "Starting FastAPI with uvicorn (workers=$FASTAPI_WORKERS)..."
  cd ../../../ignore
  setsid uv run uvicorn main:app \
    --host $HOST \
    --port $PORT \
    --workers $FASTAPI_WORKERS \
    --loop uvloop \
    --http httptools \
    --log-level error \
    >/dev/null 2>&1 &
  SERVER_PID=$!
  KILL_CMD="pkill -TERM -f 'uvicorn main:app'"
  BASE_URL="http://$HOST:$PORT"
  cd ../python/examples/testproject
elif [ "$MODE" = "django" ] || [ "$MODE" = "plain" ]; then
  # Django with Gunicorn + Uvicorn workers
  echo "Starting Django with Gunicorn + UvicornWorker (workers=$WORKERS)..."
  setsid uv run gunicorn testproject.asgi:application \
    --bind $HOST:$PORT \
    --workers $WORKERS \
    --worker-class uvicorn.workers.UvicornWorker \
    --worker-connections 1000 \
    --max-requests 10000 \
    --max-requests-jitter 1000 \
    --timeout 30 \
    --keepalive 5 \
    --preload \
    --reuse-port \
    --log-level error \
    --access-logfile - \
    --error-logfile - \
    >/dev/null 2>&1 &
  SERVER_PID=$!
  KILL_CMD="pkill -TERM -f 'gunicorn testproject.asgi:application'"
  BASE_URL="http://$HOST:$PORT/plain"
else
  # Django-Bolt
  echo "Starting Django-Bolt server..."
  DJANGO_BOLT_WORKERS=$WORKERS setsid uv run python manage.py runbolt --host $HOST --port $PORT --processes $P >/dev/null 2>&1 &
  SERVER_PID=$!
  KILL_CMD="pkill -TERM -f 'manage.py runbolt --host $HOST --port $PORT'"
  BASE_URL="http://$HOST:$PORT"
fi
sleep 2

# Sanity check: ensure 200 OK before benchmarking
CODE=$(curl -s -o /dev/null -w '%{http_code}' $BASE_URL/)
if [ "$CODE" != "200" ]; then
  echo "Expected 200 from $BASE_URL/ but got $CODE; aborting benchmark." >&2
  kill -TERM -$SERVER_PID 2>/dev/null || true
  eval $KILL_CMD 2>/dev/null || true
  exit 1
fi 

ab -k -c $C -n $N $BASE_URL/ 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"

echo ""
echo "## Response Type Endpoints"

printf "### Header Endpoint (/header)\n"
ab -k -c $C -n $N -H 'x-test: val' $BASE_URL/header 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"

printf "### Cookie Endpoint (/cookie)\n"
ab -k -c $C -n $N -H 'Cookie: session=abc' $BASE_URL/cookie 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"

printf "### Exception Endpoint (/exc)\n"
ab -k -c $C -n $N $BASE_URL/exc 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"

printf "### HTML Response (/html)\n"
ab -k -c $C -n $N $BASE_URL/html 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"

printf "### Redirect Response (/redirect)\n"
ab -k -c $C -n $N -r -H 'Accept: */*' $BASE_URL/redirect 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"

printf "### File Static via FileResponse (/file-static)\n"
ab -k -c $C -n $N $BASE_URL/file-static 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"

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
    printf "### Streaming Plain Text (/stream)\n"
    timeout "$HEY_TIMEOUT" $HEY_BIN -n $N -c $C $BASE_URL/stream 2>&1 | grep -E "(Requests/sec:|Total:|Fastest:|Slowest:|Average:|Status code distribution:)" | head -10 || echo "(stream timed out after ${HEY_TIMEOUT}s)"
    
    printf "### Server-Sent Events (/sse)\n"
    timeout "$HEY_TIMEOUT" $HEY_BIN -n $N -c $C -H "Accept: text/event-stream" $BASE_URL/sse 2>&1 | grep -E "(Requests/sec:|Total:|Fastest:|Slowest:|Average:|Status code distribution:)" | head -10 || echo "(sse timed out after ${HEY_TIMEOUT}s)"

    printf "### Server-Sent Events (async) (/sse-async)\n"
    timeout "$HEY_TIMEOUT" $HEY_BIN -n $N -c $C -H "Accept: text/event-stream" $BASE_URL/sse-async 2>&1 | grep -E "(Requests/sec:|Total:|Fastest:|Slowest:|Average:|Status code distribution:)" | head -10 || echo "(sse-async timed out after ${HEY_TIMEOUT}s)"

    printf "### OpenAI Chat Completions (stream) (/v1/chat/completions)\n"
    BODY_STREAM='{"model":"gpt-4o-mini","messages":[{"role":"user","content":"Say hi"}],"stream":true,"n_chunks":50,"token":" hi","delay_ms":0}'
    echo "$BODY_STREAM" > /tmp/bolt_chat_stream.json
    timeout "$HEY_TIMEOUT" $HEY_BIN -n $N -c $C -H "Content-Type: application/json" -m POST -D /tmp/bolt_chat_stream.json $BASE_URL/v1/chat/completions 2>&1 | grep -E "(Requests/sec:|Total:|Fastest:|Slowest:|Average:|Bytes In|Bytes Out|Status code distribution:)" | head -15 || echo "(chat stream timed out after ${HEY_TIMEOUT}s)"

    printf "### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)\n"
    BODY_STREAM_ASYNC='{"model":"gpt-4o-mini","messages":[{"role":"user","content":"Say hi"}],"stream":true,"n_chunks":50,"token":" hi","delay_ms":0}'
    echo "$BODY_STREAM_ASYNC" > /tmp/bolt_chat_stream_async.json
    timeout "$HEY_TIMEOUT" $HEY_BIN -n $N -c $C -H "Content-Type: application/json" -m POST -D /tmp/bolt_chat_stream_async.json $BASE_URL/v1/chat/completions-async 2>&1 | grep -E "(Requests/sec:|Total:|Fastest:|Slowest:|Average:|Bytes In|Bytes Out|Status code distribution:)" | head -15 || echo "(chat async stream timed out after ${HEY_TIMEOUT}s)"
else
    echo "hey not installed. Run: ./scripts/install_hey.sh"
fi

# Additional endpoint: GET /items/{item_id}
echo ""
echo "## Items GET Performance (/items/1?q=hello)"
ab -k -c $C -n $N "$BASE_URL/items/1?q=hello" 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"

# Additional endpoint: PUT /items/{item_id} with JSON body
echo ""
echo "## Items PUT JSON Performance (/items/1)"
BODY_FILE=$(mktemp)
echo '{"name":"bench","price":1.23,"is_offer":true}' > "$BODY_FILE"

if [ "$MODE" = "django" ] || [ "$MODE" = "plain" ]; then
  # Django views use different endpoint structure
  PUT_URL="$BASE_URL/items/1/update"
else
  # Django-Bolt and FastAPI use the same structure
  PUT_URL="$BASE_URL/items/1"
fi

# Sanity check: ensure PUT returns 200 OK before benchmarking
PCODE=$(curl -s -o /dev/null -w '%{http_code}' -X PUT -H 'Content-Type: application/json' --data-binary @"$BODY_FILE" $PUT_URL)
if [ "$PCODE" != "200" ]; then
  echo "Expected 200 from PUT $PUT_URL but got $PCODE; skipping Items PUT benchmark." >&2
else
  # Use -u for PUT body with ab
  ab -k -c $C -n $N -u "$BODY_FILE" -T 'application/json' $PUT_URL 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests|Non-2xx responses)"
fi
rm -f "$BODY_FILE"

kill -TERM -$SERVER_PID 2>/dev/null || true
eval $KILL_CMD 2>/dev/null || true
sleep 1

echo ""
echo "## ORM Performance"
uv run python manage.py makemigrations users --noinput >/dev/null 2>&1 || true
uv run python manage.py migrate --noinput >/dev/null 2>&1 || true

# Start server based on mode
if [ "$MODE" = "fastapi" ]; then
  cd ../../../ignore
  setsid uv run uvicorn main:app \
    --host $HOST \
    --port $PORT \
    --workers $FASTAPI_WORKERS \
    --loop uvloop \
    --http httptools \
    --log-level error \
    >/dev/null 2>&1 &
  SERVER_PID=$!
  KILL_CMD="pkill -TERM -f 'uvicorn main:app'"
  ORM_BASE_URL="http://$HOST:$PORT/users"
  cd ../python/examples/testproject
elif [ "$MODE" = "django" ] || [ "$MODE" = "plain" ]; then
  setsid uv run gunicorn testproject.asgi:application \
    --bind $HOST:$PORT \
    --workers $WORKERS \
    --worker-class uvicorn.workers.UvicornWorker \
    --preload \
    --reuse-port \
    --log-level error \
    >/dev/null 2>&1 &
  SERVER_PID=$!
  KILL_CMD="pkill -TERM -f 'gunicorn testproject.asgi:application'"
  ORM_BASE_URL="http://$HOST:$PORT/plain/users"
else
  DJANGO_BOLT_WORKERS=$WORKERS setsid uv run python manage.py runbolt --host $HOST --port $PORT --processes $P >/dev/null 2>&1 &
  SERVER_PID=$!
  KILL_CMD="pkill -TERM -f 'manage.py runbolt --host $HOST --port $PORT'"
  ORM_BASE_URL="http://$HOST:$PORT/users"
fi
sleep 2

# Sanity check
UCODE=$(curl -s -o /dev/null -w '%{http_code}' $ORM_BASE_URL/full10)
if [ "$UCODE" != "200" ]; then
  echo "Expected 200 from $ORM_BASE_URL/full10 but got $UCODE; aborting ORM benchmark." >&2
  kill -TERM -$SERVER_PID 2>/dev/null || true
  eval $KILL_CMD 2>/dev/null || true
  exit 1
fi

echo "### Users Full10 (/users/full10)"
ab -k -c $C -n $N $ORM_BASE_URL/full10 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"

echo "### Users Mini10 (/users/mini10)"
ab -k -c $C -n $N $ORM_BASE_URL/mini10 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"

kill -TERM -$SERVER_PID 2>/dev/null || true
eval $KILL_CMD 2>/dev/null || true

echo ""
echo "## Form and File Upload Performance"

# Start server for form/file tests
if [ "$MODE" = "fastapi" ]; then
  cd ../../../ignore
  setsid uv run uvicorn main:app --host $HOST --port $PORT --workers $FASTAPI_WORKERS --loop uvloop --http httptools --log-level error >/dev/null 2>&1 &
  SERVER_PID=$!
  KILL_CMD="pkill -TERM -f 'uvicorn main:app --host $HOST --port $PORT'"
  FORM_BASE_URL="http://$HOST:$PORT"
  cd ../python/examples/testproject
elif [ "$MODE" = "django" ] || [ "$MODE" = "plain" ]; then
  setsid uv run uvicorn testproject.asgi:application --host $HOST --port $PORT --workers $WORKERS --loop uvloop --http httptools --log-level error >/dev/null 2>&1 &
  SERVER_PID=$!
  KILL_CMD="pkill -TERM -f 'uvicorn testproject.asgi:application --host $HOST --port $PORT'"
  FORM_BASE_URL="http://$HOST:$PORT/plain"
else
  DJANGO_BOLT_WORKERS=$WORKERS setsid uv run python manage.py runbolt --host $HOST --port $PORT --processes $P >/dev/null 2>&1 &
  SERVER_PID=$!
  KILL_CMD="pkill -TERM -f 'manage.py runbolt --host $HOST --port $PORT'"
  FORM_BASE_URL="http://$HOST:$PORT"
fi
sleep 2

echo "### Form Data (POST /form)"
# Create form data
FORM_FILE=$(mktemp)
echo "name=TestUser&age=25&email=test%40example.com" > "$FORM_FILE"
ab -k -c $C -n $N -p "$FORM_FILE" -T 'application/x-www-form-urlencoded' $FORM_BASE_URL/form 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"
rm -f "$FORM_FILE"

echo "### File Upload (POST /upload)"
# Create a multipart form data file with proper CRLF
UPLOAD_FILE=$(mktemp)
BOUNDARY="----BoltBenchmark$(date +%s)"
printf -- "--%s\r\n" "$BOUNDARY" > "$UPLOAD_FILE"
printf "Content-Disposition: form-data; name=\"file\"; filename=\"test1.txt\"\r\n" >> "$UPLOAD_FILE"
printf "Content-Type: text/plain\r\n" >> "$UPLOAD_FILE"
printf "\r\n" >> "$UPLOAD_FILE"
printf "This is test file content 1\r\n" >> "$UPLOAD_FILE"
printf -- "--%s\r\n" "$BOUNDARY" >> "$UPLOAD_FILE"
printf "Content-Disposition: form-data; name=\"file\"; filename=\"test2.txt\"\r\n" >> "$UPLOAD_FILE"
printf "Content-Type: text/plain\r\n" >> "$UPLOAD_FILE"
printf "\r\n" >> "$UPLOAD_FILE"
printf "This is test file content 2\r\n" >> "$UPLOAD_FILE"
printf -- "--%s--\r\n" "$BOUNDARY" >> "$UPLOAD_FILE"
ab -k -c $C -n $N -p "$UPLOAD_FILE" -T "multipart/form-data; boundary=$BOUNDARY" $FORM_BASE_URL/upload 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"
rm -f "$UPLOAD_FILE"

# Mixed form with files benchmark
echo "### Mixed Form with Files (POST /mixed-form)"
MIXED_FILE=$(mktemp)
BOUNDARY="----BoltMixed$(date +%s)"
printf -- "--%s\r\n" "$BOUNDARY" > "$MIXED_FILE"
printf "Content-Disposition: form-data; name=\"title\"\r\n" >> "$MIXED_FILE"
printf "\r\n" >> "$MIXED_FILE"
printf "Test Title\r\n" >> "$MIXED_FILE"
printf -- "--%s\r\n" "$BOUNDARY" >> "$MIXED_FILE"
printf "Content-Disposition: form-data; name=\"description\"\r\n" >> "$MIXED_FILE"
printf "\r\n" >> "$MIXED_FILE"
printf "This is a test description\r\n" >> "$MIXED_FILE"
printf -- "--%s\r\n" "$BOUNDARY" >> "$MIXED_FILE"
printf "Content-Disposition: form-data; name=\"file\"; filename=\"attachment.txt\"\r\n" >> "$MIXED_FILE"
printf "Content-Type: text/plain\r\n" >> "$MIXED_FILE"
printf "\r\n" >> "$MIXED_FILE"
printf "File attachment content\r\n" >> "$MIXED_FILE"
printf -- "--%s--\r\n" "$BOUNDARY" >> "$MIXED_FILE"
ab -k -c $C -n $N -p "$MIXED_FILE" -T "multipart/form-data; boundary=$BOUNDARY" $FORM_BASE_URL/mixed-form 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"
rm -f "$MIXED_FILE"

kill -TERM -$SERVER_PID 2>/dev/null || true
eval $KILL_CMD 2>/dev/null || true

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
if [ "$MODE" = "fastapi" ]; then
  cd ../../../ignore
  setsid uv run uvicorn main:app --host $HOST --port $PORT --workers $FASTAPI_WORKERS --loop uvloop --http httptools --log-level error >/dev/null 2>&1 &
  SERVER_PID=$!
  KILL_CMD="pkill -TERM -f 'uvicorn main:app --host $HOST --port $PORT'"
  PARSE_URL="http://$HOST:$PORT/bench/parse"
  CHECK_URL="http://$HOST:$PORT/"
  cd ../python/examples/testproject
elif [ "$MODE" = "django" ] || [ "$MODE" = "plain" ]; then
  setsid uv run uvicorn testproject.asgi:application --host $HOST --port $PORT --workers $WORKERS --loop uvloop --http httptools --log-level error >/dev/null 2>&1 &
  SERVER_PID=$!
  KILL_CMD="pkill -TERM -f 'uvicorn testproject.asgi:application --host $HOST --port $PORT'"
  PARSE_URL="http://$HOST:$PORT/plain/bench/parse"
  CHECK_URL="http://$HOST:$PORT/plain/"
else
  DJANGO_BOLT_WORKERS=$WORKERS setsid uv run python manage.py runbolt --host $HOST --port $PORT --processes $P >/dev/null 2>&1 &
  SERVER_PID=$!
  KILL_CMD="pkill -TERM -f 'manage.py runbolt --host $HOST --port $PORT'"
  PARSE_URL="http://$HOST:$PORT/bench/parse"
  CHECK_URL="http://$HOST:$PORT/"
fi
sleep 2

# Sanity check
PCODE=$(curl -s -o /dev/null -w '%{http_code}' $CHECK_URL)
if [ "$PCODE" != "200" ]; then
  echo "Expected 200 from $CHECK_URL before parse test but got $PCODE; skipping." >&2
else
  ab -k -c $C -n $N -p "$BODY_FILE" -T 'application/json' $PARSE_URL 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"
fi
kill -TERM -$SERVER_PID 2>/dev/null || true
eval $KILL_CMD 2>/dev/null || true
rm -f "$BODY_FILE"


# echo "### Slow Async Operation (GET /bench/slow?ms=$SLOW_MS, c=$SLOW_CONC, t=${SLOW_DURATION}s)"
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
