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

echo "# Django-Bolt Benchmark"
echo "Generated: $(date)"
echo "Config: $P processes × $WORKERS workers | C=$C N=$N"
echo ""

echo "## Root Endpoint Performance"
cd python/examples/testproject
DJANGO_BOLT_WORKERS=$WORKERS setsid uv run python manage.py runbolt --host $HOST --port $PORT --processes $P >/dev/null 2>&1 &
SERVER_PID=$!
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

printf "### Header Endpoint (/header)\n"
ab -k -c $C -n $N -H 'x-test: val' http://$HOST:$PORT/header 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"

printf "### Cookie Endpoint (/cookie)\n"
ab -k -c $C -n $N -H 'Cookie: session=abc' http://$HOST:$PORT/cookie 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"

printf "### Exception Endpoint (/exc)\n"
ab -k -c $C -n $N http://$HOST:$PORT/exc 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"

printf "### HTML Response (/html)\n"
ab -k -c $C -n $N http://$HOST:$PORT/html 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"

printf "### Redirect Response (/redirect)\n"
ab -k -c $C -n $N -r -H 'Accept: */*' http://$HOST:$PORT/redirect 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"

printf "### File Static via FileResponse (/file-static)\n"
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
    printf "### Streaming Plain Text (/stream)\n"
    timeout "$HEY_TIMEOUT" $HEY_BIN -n $N -c $C http://$HOST:$PORT/stream 2>&1 | grep -E "(Requests/sec:|Total:|Fastest:|Slowest:|Average:|Status code distribution:)" | head -10 || echo "(stream timed out after ${HEY_TIMEOUT}s)"
    
    printf "### Server-Sent Events (/sse)\n"
    timeout "$HEY_TIMEOUT" $HEY_BIN -n $N -c $C -H "Accept: text/event-stream" http://$HOST:$PORT/sse 2>&1 | grep -E "(Requests/sec:|Total:|Fastest:|Slowest:|Average:|Status code distribution:)" | head -10 || echo "(sse timed out after ${HEY_TIMEOUT}s)"

    printf "### Server-Sent Events (async) (/sse-async)\n"
    timeout "$HEY_TIMEOUT" $HEY_BIN -n $N -c $C -H "Accept: text/event-stream" http://$HOST:$PORT/sse-async 2>&1 | grep -E "(Requests/sec:|Total:|Fastest:|Slowest:|Average:|Status code distribution:)" | head -10 || echo "(sse-async timed out after ${HEY_TIMEOUT}s)"

    printf "### OpenAI Chat Completions (stream) (/v1/chat/completions)\n"
    BODY_STREAM='{"model":"gpt-4o-mini","messages":[{"role":"user","content":"Say hi"}],"stream":true,"n_chunks":50,"token":" hi","delay_ms":0}'
    echo "$BODY_STREAM" > /tmp/bolt_chat_stream.json
    timeout "$HEY_TIMEOUT" $HEY_BIN -n $N -c $C -H "Content-Type: application/json" -m POST -D /tmp/bolt_chat_stream.json http://$HOST:$PORT/v1/chat/completions 2>&1 | grep -E "(Requests/sec:|Total:|Fastest:|Slowest:|Average:|Bytes In|Bytes Out|Status code distribution:)" | head -15 || echo "(chat stream timed out after ${HEY_TIMEOUT}s)"

    printf "### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)\n"
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

DJANGO_BOLT_WORKERS=$WORKERS setsid uv run python manage.py runbolt --host $HOST --port $PORT --processes $P >/dev/null 2>&1 &
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

echo "### Users Mini10 (/users/mini10)"
ab -k -c $C -n $N http://$HOST:$PORT/users/mini10 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"

kill -TERM -$SERVER_PID 2>/dev/null || true
pkill -TERM -f "manage.py runbolt --host $HOST --port $PORT" 2>/dev/null || true

echo ""
echo "## Class-Based Views (CBV) Performance"

DJANGO_BOLT_WORKERS=$WORKERS setsid uv run python manage.py runbolt --host $HOST --port $PORT --processes $P >/dev/null 2>&1 &
SERVER_PID=$!
sleep 2

echo "### Simple APIView GET (/cbv-simple)"
ab -k -c $C -n $N http://$HOST:$PORT/cbv-simple 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"

echo "### Simple APIView POST (/cbv-simple)"
BODY_FILE=$(mktemp)
echo '{"name":"bench","price":1.23,"is_offer":true}' > "$BODY_FILE"
ab -k -c $C -n $N -p "$BODY_FILE" -T 'application/json' http://$HOST:$PORT/cbv-simple 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"
rm -f "$BODY_FILE"

echo "### Items100 ViewSet GET (/cbv-items100)"
ab -k -c $C -n $N http://$HOST:$PORT/cbv-items100 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"

echo ""
echo "## CBV ViewSet - Full CRUD Operations"

echo "### ItemViewSet GET (Retrieve) (/cbv-items-vs/1)"
ab -k -c $C -n $N http://$HOST:$PORT/cbv-items-vs/1 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"

echo "### ItemViewSet POST (Create) (/cbv-items-vs/1)"
BODY_FILE=$(mktemp)
echo '{"name":"new-item","price":99.99,"is_offer":false}' > "$BODY_FILE"
PCODE=$(curl -s -o /dev/null -w '%{http_code}' -X POST -H 'Content-Type: application/json' --data-binary @"$BODY_FILE" http://$HOST:$PORT/cbv-items-vs/1)
if [ "$PCODE" = "200" ] || [ "$PCODE" = "201" ]; then
  ab -k -c $C -n $N -p "$BODY_FILE" -T 'application/json' http://$HOST:$PORT/cbv-items-vs/1 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"
else
  echo "Skipped: POST returned $PCODE" >&2
fi
rm -f "$BODY_FILE"

echo "### ItemViewSet PUT (Update Full) (/cbv-items-vs/1)"
BODY_FILE=$(mktemp)
echo '{"name":"updated-item","price":79.99,"is_offer":true}' > "$BODY_FILE"
PCODE=$(curl -s -o /dev/null -w '%{http_code}' -X PUT -H 'Content-Type: application/json' --data-binary @"$BODY_FILE" http://$HOST:$PORT/cbv-items-vs/1)
if [ "$PCODE" = "200" ]; then
  ab -k -c $C -n $N -u "$BODY_FILE" -T 'application/json' http://$HOST:$PORT/cbv-items-vs/1 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"
else
  echo "Skipped: PUT returned $PCODE" >&2
fi
rm -f "$BODY_FILE"

echo "### ItemViewSet PATCH (Update Partial) (/cbv-items-vs/1)"
BODY_FILE=$(mktemp)
echo '{"name":"patched-item","price":59.99,"is_offer":false}' > "$BODY_FILE"
PCODE=$(curl -s -o /dev/null -w '%{http_code}' -X PATCH -H 'Content-Type: application/json' --data-binary @"$BODY_FILE" http://$HOST:$PORT/cbv-items-vs/1)
if [ "$PCODE" = "200" ]; then
  # ab doesn't support PATCH, use hey if available
  if [ -n "$HEY_BIN" ]; then
    echo '{"name":"patched-item","price":59.99,"is_offer":false}' > /tmp/bolt_patch.json
    timeout "$HEY_TIMEOUT" $HEY_BIN -n $N -c $C -m PATCH -H "Content-Type: application/json" -D /tmp/bolt_patch.json http://$HOST:$PORT/cbv-items-vs/1 2>&1 | grep -E "(Requests/sec:|Total:|Fastest:|Slowest:|Average:|Status code distribution:)" | head -10 || echo "(patch timed out after ${HEY_TIMEOUT}s)"
    rm -f /tmp/bolt_patch.json
  else
    echo "Skipped: PATCH requires 'hey' tool" >&2
  fi
else
  echo "Skipped: PATCH returned $PCODE" >&2
fi
rm -f "$BODY_FILE"

echo "### ItemViewSet DELETE (Destroy) (/cbv-items-vs/999)"
# Use hey for DELETE if available, otherwise skip (ab has issues with DELETE)
if [ -n "$HEY_BIN" ]; then
  DCODE=$(curl -s -o /dev/null -w '%{http_code}' -X DELETE http://$HOST:$PORT/cbv-items-vs/999)
  if [ "$DCODE" = "200" ] || [ "$DCODE" = "204" ]; then
    timeout "$HEY_TIMEOUT" $HEY_BIN -n $N -c $C -m DELETE http://$HOST:$PORT/cbv-items-vs/999 2>&1 | grep -E "(Requests/sec:|Total:|Fastest:|Slowest:|Average:|Status code distribution:)" | head -10 || echo "(delete timed out after ${HEY_TIMEOUT}s)"
  else
    echo "Skipped: DELETE returned $DCODE" >&2
  fi
else
  echo "Skipped: DELETE requires 'hey' tool" >&2
fi

echo "### ItemViewSet HEAD (/cbv-items-vs/1)"
# HEAD request
HCODE=$(curl -s -o /dev/null -w '%{http_code}' -I http://$HOST:$PORT/cbv-items-vs/1)
if [ "$HCODE" = "200" ]; then
  ab -k -c $C -n $N -i http://$HOST:$PORT/cbv-items-vs/1 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"
else
  echo "Skipped: HEAD returned $HCODE" >&2
fi

echo "### ItemViewSet OPTIONS (/cbv-items-vs)"
# OPTIONS request
OCODE=$(curl -s -o /dev/null -w '%{http_code}' -X OPTIONS http://$HOST:$PORT/cbv-items-vs)
if [ "$OCODE" = "200" ]; then
  if [ -n "$HEY_BIN" ]; then
    timeout "$HEY_TIMEOUT" $HEY_BIN -n $N -c $C -m OPTIONS http://$HOST:$PORT/cbv-items-vs 2>&1 | grep -E "(Requests/sec:|Total:|Fastest:|Slowest:|Average:|Status code distribution:)" | head -10 || echo "(options timed out after ${HEY_TIMEOUT}s)"
  else
    echo "Skipped: OPTIONS requires 'hey' tool" >&2
  fi
else
  echo "Skipped: OPTIONS returned $OCODE" >&2
fi

echo ""
echo "## CBV Custom Actions"

echo "### Custom Action: Publish (/cbv-items-vs/1/publish)"
PCODE=$(curl -s -o /dev/null -w '%{http_code}' -X POST http://$HOST:$PORT/cbv-items-vs/1/publish)
if [ "$PCODE" = "200" ]; then
  ab -k -c $C -n $N -p /dev/null -T 'application/json' http://$HOST:$PORT/cbv-items-vs/1/publish 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"
else
  echo "Skipped: Publish returned $PCODE" >&2
fi

echo "### Custom Action: Archive (/cbv-items-vs/1/archive)"
ACODE=$(curl -s -o /dev/null -w '%{http_code}' -X POST http://$HOST:$PORT/cbv-items-vs/1/archive)
if [ "$ACODE" = "200" ]; then
  ab -k -c $C -n $N -p /dev/null -T 'application/json' http://$HOST:$PORT/cbv-items-vs/1/archive 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"
else
  echo "Skipped: Archive returned $ACODE" >&2
fi

echo "### Custom Action: Search (/cbv-items-vs/search?query=test)"
SCODE=$(curl -s -o /dev/null -w '%{http_code}' "http://$HOST:$PORT/cbv-items-vs/search?query=test")
if [ "$SCODE" = "200" ]; then
  ab -k -c $C -n $N "http://$HOST:$PORT/cbv-items-vs/search?query=test" 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"
else
  echo "Skipped: Search returned $SCODE" >&2
fi

echo ""
echo "## CBV Additional Benchmarks"

echo "### CBV Bench Parse (POST /cbv-bench-parse)"
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
ab -k -c $C -n $N -p "$BODY_FILE" -T 'application/json' http://$HOST:$PORT/cbv-bench-parse 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"
rm -f "$BODY_FILE"

echo "### CBV Response Types (/cbv-response)"
ab -k -c $C -n $N http://$HOST:$PORT/cbv-response 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"

# Streaming and SSE tests for CBV
if [ -n "$HEY_BIN" ]; then
    echo "### CBV Streaming Plain Text (/cbv-stream)"
    timeout "$HEY_TIMEOUT" $HEY_BIN -n $N -c $C http://$HOST:$PORT/cbv-stream 2>&1 | grep -E "(Requests/sec:|Total:|Fastest:|Slowest:|Average:|Status code distribution:)" | head -10 || echo "(cbv-stream timed out after ${HEY_TIMEOUT}s)"

    echo "### CBV Server-Sent Events (/cbv-sse)"
    timeout "$HEY_TIMEOUT" $HEY_BIN -n $N -c $C -H "Accept: text/event-stream" http://$HOST:$PORT/cbv-sse 2>&1 | grep -E "(Requests/sec:|Total:|Fastest:|Slowest:|Average:|Status code distribution:)" | head -10 || echo "(cbv-sse timed out after ${HEY_TIMEOUT}s)"

    echo "### CBV Chat Completions (stream) (/cbv-chat-completions)"
    BODY_STREAM='{"model":"gpt-4o-mini","messages":[{"role":"user","content":"Say hi"}],"stream":true,"n_chunks":50,"token":" hi","delay_ms":0}'
    echo "$BODY_STREAM" > /tmp/bolt_cbv_chat_stream.json
    timeout "$HEY_TIMEOUT" $HEY_BIN -n $N -c $C -H "Content-Type: application/json" -m POST -D /tmp/bolt_cbv_chat_stream.json http://$HOST:$PORT/cbv-chat-completions 2>&1 | grep -E "(Requests/sec:|Total:|Fastest:|Slowest:|Average:|Bytes In|Bytes Out|Status code distribution:)" | head -15 || echo "(cbv-chat stream timed out after ${HEY_TIMEOUT}s)"
    rm -f /tmp/bolt_cbv_chat_stream.json
fi

# ORM endpoints with CBV
echo ""
echo "## ORM Performance with CBV"

# Sanity check
UCODE=$(curl -s -o /dev/null -w '%{http_code}' http://$HOST:$PORT/users/cbv-mini10)
if [ "$UCODE" != "200" ]; then
  echo "Expected 200 from /users/cbv-mini10 but got $UCODE; skipping CBV ORM benchmark." >&2
else
  echo "### Users CBV Mini10 (List) (/users/cbv-mini10)"
  ab -k -c $C -n $N http://$HOST:$PORT/users/cbv-mini10 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"
fi

echo "### Users CBV List with Filter (/users/cbv-users?active=true&limit=10)"
LCODE=$(curl -s -o /dev/null -w '%{http_code}' "http://$HOST:$PORT/users/cbv-users?active=true&limit=10")
if [ "$LCODE" = "200" ]; then
  ab -k -c $C -n $N "http://$HOST:$PORT/users/cbv-users?active=true&limit=10" 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"
else
  echo "Skipped: List returned $LCODE" >&2
fi

echo "### Users CBV Stats (/users/stats)"
SCODE=$(curl -s -o /dev/null -w '%{http_code}' http://$HOST:$PORT/users/stats)
if [ "$SCODE" = "200" ]; then
  ab -k -c $C -n $N http://$HOST:$PORT/users/stats 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"
else
  echo "Skipped: Stats returned $SCODE" >&2
fi

echo ""
echo "## CBV User CRUD Operations (ORM)"

# Create a test user first for benchmarking
echo "### Setting up test user for benchmarks..."
BODY_FILE=$(mktemp)
echo '{"username":"benchmark_user","email":"benchmark@example.com","first_name":"Benchmark","last_name":"User"}' > "$BODY_FILE"
USER_RESPONSE=$(curl -s -X POST -H 'Content-Type: application/json' --data-binary @"$BODY_FILE" http://$HOST:$PORT/users/cbv-users/0)
TEST_USER_ID=$(echo "$USER_RESPONSE" | grep -o '"id":[0-9]*' | grep -o '[0-9]*' | head -1)
rm -f "$BODY_FILE"

if [ -z "$TEST_USER_ID" ]; then
  echo "Failed to create test user, skipping User CRUD benchmarks" >&2
  TEST_USER_ID=1
fi
echo "Test user created with ID: $TEST_USER_ID"

echo "### UserViewSet GET (Retrieve) (/users/cbv-users/$TEST_USER_ID)"
GCODE=$(curl -s -o /dev/null -w '%{http_code}' http://$HOST:$PORT/users/cbv-users/$TEST_USER_ID)
if [ "$GCODE" = "200" ]; then
  ab -k -c $C -n $N http://$HOST:$PORT/users/cbv-users/$TEST_USER_ID 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"
else
  echo "Skipped: User GET returned $GCODE" >&2
fi

echo "### UserViewSet POST (Create) (/users/cbv-users/0)"
# Note: Skipping due to unique username constraints - see BenchItem POST instead
echo "Skipped: POST uses BenchItem model instead (no unique constraints)" >&2

echo "### UserViewSet PUT (Update Full) (/users/cbv-users/$TEST_USER_ID)"
BODY_FILE=$(mktemp)
echo '{"email":"updated@example.com","first_name":"Updated","last_name":"User","is_active":true}' > "$BODY_FILE"
PUCODE=$(curl -s -o /dev/null -w '%{http_code}' -X PUT -H 'Content-Type: application/json' --data-binary @"$BODY_FILE" http://$HOST:$PORT/users/cbv-users/$TEST_USER_ID)
if [ "$PUCODE" = "200" ]; then
  ab -k -c $C -n $N -u "$BODY_FILE" -T 'application/json' http://$HOST:$PORT/users/cbv-users/$TEST_USER_ID 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"
else
  echo "Skipped: User PUT returned $PUCODE" >&2
fi
rm -f "$BODY_FILE"

echo "### UserViewSet PATCH (Update Partial) (/users/cbv-users/$TEST_USER_ID)"
BODY_FILE=$(mktemp)
echo '{"email":"patched@example.com","first_name":"Patched"}' > "$BODY_FILE"
PACODE=$(curl -s -o /dev/null -w '%{http_code}' -X PATCH -H 'Content-Type: application/json' --data-binary @"$BODY_FILE" http://$HOST:$PORT/users/cbv-users/$TEST_USER_ID)
if [ "$PACODE" = "200" ]; then
  if [ -n "$HEY_BIN" ]; then
    timeout "$HEY_TIMEOUT" $HEY_BIN -n $N -c $C -m PATCH -H "Content-Type: application/json" -D "$BODY_FILE" http://$HOST:$PORT/users/cbv-users/$TEST_USER_ID 2>&1 | grep -E "(Requests/sec:|Total:|Fastest:|Slowest:|Average:|Status code distribution:)" | head -10 || echo "(user patch timed out after ${HEY_TIMEOUT}s)"
  else
    echo "Skipped: PATCH requires 'hey' tool" >&2
  fi
else
  echo "Skipped: User PATCH returned $PACODE" >&2
fi
rm -f "$BODY_FILE"

echo ""
echo "## CBV BenchItem CRUD Operations (ORM - No Unique Constraints)"

# Create a test item first for benchmarking
echo "### Setting up test bench item for CRUD benchmarks..."
BODY_FILE=$(mktemp)
echo '{"name":"benchmark_item","value":100,"description":"Item for benchmarking","is_active":true}' > "$BODY_FILE"
ITEM_RESPONSE=$(curl -s -X POST -H 'Content-Type: application/json' --data-binary @"$BODY_FILE" http://$HOST:$PORT/bench/bench-items/0)
TEST_ITEM_ID=$(echo "$ITEM_RESPONSE" | grep -o '"id":[0-9]*' | grep -o '[0-9]*' | head -1)
rm -f "$BODY_FILE"

if [ -z "$TEST_ITEM_ID" ]; then
  echo "Failed to create test bench item, skipping Bench CRUD benchmarks" >&2
  TEST_ITEM_ID=1
fi
echo "Test bench item created with ID: $TEST_ITEM_ID"

echo "### BenchItemViewSet GET (Retrieve) (/bench/bench-items/$TEST_ITEM_ID)"
GCODE=$(curl -s -o /dev/null -w '%{http_code}' http://$HOST:$PORT/bench/bench-items/$TEST_ITEM_ID)
if [ "$GCODE" = "200" ]; then
  ab -k -c $C -n $N http://$HOST:$PORT/bench/bench-items/$TEST_ITEM_ID 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"
else
  echo "Skipped: BenchItem GET returned $GCODE" >&2
fi

echo "### BenchItemViewSet POST (Create) (/bench/bench-items/0)"
BODY_FILE=$(mktemp)
echo '{"name":"bench_item","value":42,"description":"Benchmarking POST","is_active":true}' > "$BODY_FILE"
PCODE=$(curl -s -o /dev/null -w '%{http_code}' -X POST -H 'Content-Type: application/json' --data-binary @"$BODY_FILE" http://$HOST:$PORT/bench/bench-items/0)
if [ "$PCODE" = "200" ] || [ "$PCODE" = "201" ]; then
  # No unique constraints - all POST requests should succeed
  ab -k -c $C -n $N -p "$BODY_FILE" -T 'application/json' http://$HOST:$PORT/bench/bench-items/0 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"
else
  echo "Skipped: BenchItem POST returned $PCODE" >&2
fi
rm -f "$BODY_FILE"

echo "### BenchItemViewSet PUT (Update Full) (/bench/bench-items/$TEST_ITEM_ID)"
BODY_FILE=$(mktemp)
echo '{"name":"updated_item","value":200,"description":"Updated via PUT","is_active":true}' > "$BODY_FILE"
PUCODE=$(curl -s -o /dev/null -w '%{http_code}' -X PUT -H 'Content-Type: application/json' --data-binary @"$BODY_FILE" http://$HOST:$PORT/bench/bench-items/$TEST_ITEM_ID)
if [ "$PUCODE" = "200" ]; then
  ab -k -c $C -n $N -u "$BODY_FILE" -T 'application/json' http://$HOST:$PORT/bench/bench-items/$TEST_ITEM_ID 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"
else
  echo "Skipped: BenchItem PUT returned $PUCODE" >&2
fi
rm -f "$BODY_FILE"

echo "### BenchItemViewSet PATCH (Update Partial) (/bench/bench-items/$TEST_ITEM_ID)"
BODY_FILE=$(mktemp)
echo '{"name":"patched_item","value":300}' > "$BODY_FILE"
PACODE=$(curl -s -o /dev/null -w '%{http_code}' -X PATCH -H 'Content-Type: application/json' --data-binary @"$BODY_FILE" http://$HOST:$PORT/bench/bench-items/$TEST_ITEM_ID)
if [ "$PACODE" = "200" ]; then
  if [ -n "$HEY_BIN" ]; then
    timeout "$HEY_TIMEOUT" $HEY_BIN -n $N -c $C -m PATCH -H "Content-Type: application/json" -D "$BODY_FILE" http://$HOST:$PORT/bench/bench-items/$TEST_ITEM_ID 2>&1 | grep -E "(Requests/sec:|Total:|Fastest:|Slowest:|Average:|Status code distribution:)" | head -10 || echo "(bench patch timed out after ${HEY_TIMEOUT}s)"
  else
    echo "Skipped: PATCH requires 'hey' tool" >&2
  fi
else
  echo "Skipped: BenchItem PATCH returned $PACODE" >&2
fi
rm -f "$BODY_FILE"

echo ""
echo "## CBV User Custom Actions"

echo "### Custom Action: Activate User (/users/cbv-users/$TEST_USER_ID/activate)"
ACODE=$(curl -s -o /dev/null -w '%{http_code}' -X POST http://$HOST:$PORT/users/cbv-users/$TEST_USER_ID/activate)
if [ "$ACODE" = "200" ]; then
  ab -k -c $C -n $N -p /dev/null -T 'application/json' http://$HOST:$PORT/users/cbv-users/$TEST_USER_ID/activate 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"
else
  echo "Skipped: Activate returned $ACODE" >&2
fi

echo "### Custom Action: Deactivate User (/users/cbv-users/$TEST_USER_ID/deactivate)"
DCODE=$(curl -s -o /dev/null -w '%{http_code}' -X POST http://$HOST:$PORT/users/cbv-users/$TEST_USER_ID/deactivate)
if [ "$DCODE" = "200" ]; then
  ab -k -c $C -n $N -p /dev/null -T 'application/json' http://$HOST:$PORT/users/cbv-users/$TEST_USER_ID/deactivate 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"
else
  echo "Skipped: Deactivate returned $DCODE" >&2
fi

echo "### Custom Action: Search Users (/users/cbv-users/search?query=benchmark)"
SCODE=$(curl -s -o /dev/null -w '%{http_code}' "http://$HOST:$PORT/users/cbv-users/search?query=benchmark")
if [ "$SCODE" = "200" ]; then
  ab -k -c $C -n $N "http://$HOST:$PORT/users/cbv-users/search?query=benchmark" 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"
else
  echo "Skipped: User Search returned $SCODE" >&2
fi

kill -TERM -$SERVER_PID 2>/dev/null || true
pkill -TERM -f "manage.py runbolt --host $HOST --port $PORT" 2>/dev/null || true

echo ""
echo "## Form and File Upload Performance"

# Start server for form/file tests
DJANGO_BOLT_WORKERS=$WORKERS setsid uv run python manage.py runbolt --host $HOST --port $PORT --processes $P >/dev/null 2>&1 &
SERVER_PID=$!
sleep 2

echo "### Form Data (POST /form)"
# Create form data
FORM_FILE=$(mktemp)
echo "name=TestUser&age=25&email=test%40example.com" > "$FORM_FILE"
ab -k -c $C -n $N -p "$FORM_FILE" -T 'application/x-www-form-urlencoded' http://$HOST:$PORT/form 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"
rm -f "$FORM_FILE"

echo "### File Upload (POST /upload)"
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
echo "### Mixed Form with Files (POST /mixed-form)"
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
DJANGO_BOLT_WORKERS=$WORKERS setsid uv run python manage.py runbolt --host $HOST --port $PORT --processes $P >/dev/null 2>&1 &
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


