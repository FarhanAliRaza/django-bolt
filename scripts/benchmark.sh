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
cd python/example
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
echo "## 10kb JSON Response Performance"

printf "### 10kb JSON (Async) (/10k-json)\n"
ab -k -c $C -n $N http://$HOST:$PORT/10k-json 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"

printf "### 10kb JSON (Sync) (/sync-10k-json)\n"
ab -k -c $C -n $N http://$HOST:$PORT/sync-10k-json 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"

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

echo ""
echo "## Authentication & Authorization Performance"

# Create a Django user and JWT token for testing
TOKEN=$(uv run python << 'PYTHON_TOKEN_SCRIPT'
import os
import sys
import jwt
import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testproject.settings')

try:
    import django
    django.setup()

    from django.conf import settings
    from django.contrib.auth.models import User

    # Get or create a test user
    user, created = User.objects.get_or_create(
        username='benchuser',
        defaults={'email': 'bench@example.com'}
    )

    # Create JWT token with correct user ID
    payload = {
        'sub': str(user.id),
        'exp': int(time.time()) + 3600,
        'iat': int(time.time()),
        'is_staff': user.is_staff,
        'is_superuser': user.is_superuser,
        'username': user.username,
        'email': user.email
    }

    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    print(token)
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
PYTHON_TOKEN_SCRIPT
2>/dev/null)

# Only run auth tests if we have a valid token
if [ -n "$TOKEN" ] && [ ${#TOKEN} -gt 50 ]; then
    AUTH_HEADER="Authorization: Bearer $TOKEN"

    printf "### Auth NO User Access (/auth/no-user-access) - lazy loading, no DB query\n"
    ab -k -c $C -n $N -H "$AUTH_HEADER" http://$HOST:$PORT/auth/no-user-access 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"

    printf "### Get Authenticated User (/auth/me) - accesses request.user, triggers DB query\n"
    ab -k -c $C -n $N -H "$AUTH_HEADER" http://$HOST:$PORT/auth/me 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"

    printf "### Get User via Dependency (/auth/me-dependency)\n"
    ab -k -c $C -n $N -H "$AUTH_HEADER" http://$HOST:$PORT/auth/me-dependency 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"

    printf "### Get Auth Context (/auth/context) validated jwt no db\n"
    ab -k -c $C -n $N -H "$AUTH_HEADER" http://$HOST:$PORT/auth/context 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"
else
    echo "Skipped auth benchmarks: Could not generate JWT token"
fi

# Streaming and SSE tests using hey (better than ab for streaming)
echo ""
echo "## Streaming and SSE Performance"
echo "SEE STREAMING_BENCHMARK_DEV.md"
# Check if hey is available
# HEY_BIN=""
# if command -v hey &> /dev/null; then
#     HEY_BIN="hey"
# elif [ -f "$HOME/go/bin/hey" ]; then
#     HEY_BIN="$HOME/go/bin/hey"
# elif [ -f "$HOME/.local/bin/hey" ]; then
#     HEY_BIN="$HOME/.local/bin/hey"
# fi

# if [ -n "$HEY_BIN" ]; then
#     printf "### Streaming Plain Text (Async) (/stream)\n"
#     timeout "$HEY_TIMEOUT" $HEY_BIN -n $N -c $C http://$HOST:$PORT/stream 2>&1 | grep -E "(Requests/sec:|Total:|Fastest:|Slowest:|Average:|Status code distribution:)" | head -10 || echo "(stream timed out after ${HEY_TIMEOUT}s)"

#     printf "### Streaming Plain Text (Sync) (/sync-stream)\n"
#     timeout "$HEY_TIMEOUT" $HEY_BIN -n $N -c $C http://$HOST:$PORT/sync-stream 2>&1 | grep -E "(Requests/sec:|Total:|Fastest:|Slowest:|Average:|Status code distribution:)" | head -10 || echo "(sync-stream timed out after ${HEY_TIMEOUT}s)"

#     printf "### Server-Sent Events (Async) (/sse)\n"
#     timeout "$HEY_TIMEOUT" $HEY_BIN -n $N -c $C -H "Accept: text/event-stream" http://$HOST:$PORT/sse 2>&1 | grep -E "(Requests/sec:|Total:|Fastest:|Slowest:|Average:|Status code distribution:)" | head -10 || echo "(sse timed out after ${HEY_TIMEOUT}s)"

#     printf "### Server-Sent Events (Sync) (/sync-sse)\n"
#     timeout "$HEY_TIMEOUT" $HEY_BIN -n $N -c $C -H "Accept: text/event-stream" http://$HOST:$PORT/sync-sse 2>&1 | grep -E "(Requests/sec:|Total:|Fastest:|Slowest:|Average:|Status code distribution:)" | head -10 || echo "(sync-sse timed out after ${HEY_TIMEOUT}s)"

#     printf "### Server-Sent Events (Async Generator) (/sse-async)\n"
#     timeout "$HEY_TIMEOUT" $HEY_BIN -n $N -c $C -H "Accept: text/event-stream" http://$HOST:$PORT/sse-async 2>&1 | grep -E "(Requests/sec:|Total:|Fastest:|Slowest:|Average:|Status code distribution:)" | head -10 || echo "(sse-async timed out after ${HEY_TIMEOUT}s)"

#     printf "### OpenAI Chat Completions (stream) (/v1/chat/completions)\n"
#     BODY_STREAM='{"model":"gpt-4o-mini","messages":[{"role":"user","content":"Say hi"}],"stream":true,"n_chunks":50,"token":" hi","delay_ms":0}'
#     echo "$BODY_STREAM" > /tmp/bolt_chat_stream.json
#     timeout "$HEY_TIMEOUT" $HEY_BIN -n $N -c $C -H "Content-Type: application/json" -m POST -D /tmp/bolt_chat_stream.json http://$HOST:$PORT/v1/chat/completions 2>&1 | grep -E "(Requests/sec:|Total:|Fastest:|Slowest:|Average:|Bytes In|Bytes Out|Status code distribution:)" | head -15 || echo "(chat stream timed out after ${HEY_TIMEOUT}s)"

#     printf "### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)\n"
#     BODY_STREAM_ASYNC='{"model":"gpt-4o-mini","messages":[{"role":"user","content":"Say hi"}],"stream":true,"n_chunks":50,"token":" hi","delay_ms":0}'
#     echo "$BODY_STREAM_ASYNC" > /tmp/bolt_chat_stream_async.json
#     timeout "$HEY_TIMEOUT" $HEY_BIN -n $N -c $C -H "Content-Type: application/json" -m POST -D /tmp/bolt_chat_stream_async.json http://$HOST:$PORT/v1/chat/completions-async 2>&1 | grep -E "(Requests/sec:|Total:|Fastest:|Slowest:|Average:|Bytes In|Bytes Out|Status code distribution:)" | head -15 || echo "(chat async stream timed out after ${HEY_TIMEOUT}s)"
# else
#     echo "hey not installed. Run: ./scripts/install_hey.sh"
# fi

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

# Seed users for benchmarking (create 1000 test users)
echo "Seeding 1000 users for benchmark..."
SEED_CODE=$(curl -s -o /dev/null -w '%{http_code}' -X GET http://$HOST:$PORT/users/seed?count=1000)
if [ "$SEED_CODE" != "200" ]; then
  echo "Warning: Failed to seed users (got $SEED_CODE), benchmarking with empty database" >&2
else
  echo "Successfully seeded users"

  # Validate users exist by checking /users/full10
  USERS_RESPONSE=$(curl -s http://$HOST:$PORT/users/full10)
  USER_COUNT=$(echo "$USERS_RESPONSE" | grep -o '"id"' | wc -l)
  if [ "$USER_COUNT" -eq 0 ]; then
    echo "Warning: No users found after seeding, benchmarking with empty database" >&2
  else
    echo "Validated: $USER_COUNT users exist in database"
  fi
fi

echo "### Users Full10 (Async) (/users/full10)"
ab -k -c $C -n $N http://$HOST:$PORT/users/full10 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"

echo "### Users Full10 (Sync) (/users/sync-full10)"
ab -k -c $C -n $N http://$HOST:$PORT/users/sync-full10 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"

echo "### Users Mini10 (Async) (/users/mini10)"
ab -k -c $C -n $N http://$HOST:$PORT/users/mini10 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"

echo "### Users Mini10 (Sync) (/users/sync-mini10)"
ab -k -c $C -n $N http://$HOST:$PORT/users/sync-mini10 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"

# Clean up: delete all users
echo "Cleaning up test users..."
curl -s -X POST http://$HOST:$PORT/users/delete >/dev/null 2>&1

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
echo "## CBV Items - Basic Operations"

echo "### CBV Items GET (Retrieve) (/cbv-items/1)"
GCODE=$(curl -s -o /dev/null -w '%{http_code}' "http://$HOST:$PORT/cbv-items/1?q=test")
if [ "$GCODE" = "200" ]; then
  ab -k -c $C -n $N "http://$HOST:$PORT/cbv-items/1?q=test" 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"
else
  echo "Skipped: CBV Items GET returned $GCODE" >&2
fi

echo "### CBV Items PUT (Update) (/cbv-items/1)"
BODY_FILE=$(mktemp)
echo '{"name":"updated-item","price":79.99,"is_offer":true}' > "$BODY_FILE"
PCODE=$(curl -s -o /dev/null -w '%{http_code}' -X PUT -H 'Content-Type: application/json' --data-binary @"$BODY_FILE" http://$HOST:$PORT/cbv-items/1)
if [ "$PCODE" = "200" ]; then
  ab -k -c $C -n $N -u "$BODY_FILE" -T 'application/json' http://$HOST:$PORT/cbv-items/1 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"
else
  echo "Skipped: CBV Items PUT returned $PCODE" >&2
fi
rm -f "$BODY_FILE"

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

# Seed users for CBV benchmarking
echo "Seeding 1000 users for CBV benchmark..."
SEED_CODE=$(curl -s -o /dev/null -w '%{http_code}' -X GET http://$HOST:$PORT/users/seed?count=1000)
if [ "$SEED_CODE" != "200" ]; then
  echo "Warning: Failed to seed users (got $SEED_CODE), benchmarking with empty database" >&2
else
  echo "Successfully seeded users"

  # Validate users exist by checking /users/cbv-mini10
  USERS_RESPONSE=$(curl -s http://$HOST:$PORT/users/cbv-mini10)
  USER_COUNT=$(echo "$USERS_RESPONSE" | grep -o '"id"' | wc -l)
  if [ "$USER_COUNT" -eq 0 ]; then
    echo "Warning: No users found after seeding, benchmarking with empty database" >&2
  else
    echo "Validated: $USER_COUNT users exist in database"
  fi
fi

# Sanity check
UCODE=$(curl -s -o /dev/null -w '%{http_code}' http://$HOST:$PORT/users/cbv-mini10)
if [ "$UCODE" != "200" ]; then
  echo "Expected 200 from /users/cbv-mini10 but got $UCODE; skipping CBV ORM benchmark." >&2
else
  echo "### Users CBV Mini10 (List) (/users/cbv-mini10)"
  ab -k -c $C -n $N http://$HOST:$PORT/users/cbv-mini10 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"
fi

# Clean up: delete all users
echo "Cleaning up test users..."
curl -s -X POST http://$HOST:$PORT/users/delete >/dev/null 2>&1

echo ""

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
# Create a multipart form data file with proper CRLF line endings
UPLOAD_FILE=$(mktemp)
BOUNDARY="----BoltBenchmark$(date +%s)"
# Use printf with \r\n for proper CRLF line endings (required by HTTP multipart/form-data spec)
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
ab -k -c $C -n $N -p "$UPLOAD_FILE" -T "multipart/form-data; boundary=$BOUNDARY" http://$HOST:$PORT/upload 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"
rm -f "$UPLOAD_FILE"

# Mixed form with files benchmark
echo "### Mixed Form with Files (POST /mixed-form)"
MIXED_FILE=$(mktemp)
BOUNDARY="----BoltMixed$(date +%s)"
# Use printf with \r\n for proper CRLF line endings (required by HTTP multipart/form-data spec)
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
ab -k -c $C -n $N -p "$MIXED_FILE" -T "multipart/form-data; boundary=$BOUNDARY" http://$HOST:$PORT/mixed-form 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"
rm -f "$MIXED_FILE"

kill -TERM -$SERVER_PID 2>/dev/null || true
pkill -TERM -f "manage.py runbolt --host $HOST --port $PORT" 2>/dev/null || true

echo ""
echo "## Django Middleware Performance"

# Start server for middleware test
DJANGO_BOLT_WORKERS=$WORKERS setsid uv run python manage.py runbolt --host $HOST --port $PORT --processes $P >/dev/null 2>&1 &
SERVER_PID=$!
sleep 2

# Sanity check middleware endpoint
MCODE=$(curl -s -o /dev/null -w '%{http_code}' http://$HOST:$PORT/middleware/demo)
if [ "$MCODE" != "200" ]; then
  echo "Expected 200 from /middleware/demo but got $MCODE; skipping middleware benchmark." >&2
else
  echo "### Django Middleware + Messages Framework (/middleware/demo)"
  echo "Tests: SessionMiddleware, AuthenticationMiddleware, MessageMiddleware, custom middleware, template rendering"
  ab -k -c $C -n $N http://$HOST:$PORT/middleware/demo 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"
fi

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
rm -f "$BODY_FILE"

echo ""
echo "## Serializer Performance Benchmarks"

# Test raw msgspec (baseline)
SERIALIZER_RAW=$(mktemp)
cat > "$SERIALIZER_RAW" << 'JSON'
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "bio": "Software developer"
}
JSON

echo "### Raw msgspec Serializer (POST /bench/serializer-raw)"
ab -k -c $C -n $N -p "$SERIALIZER_RAW" -T 'application/json' http://$HOST:$PORT/bench/serializer-raw 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"
rm -f "$SERIALIZER_RAW"

# Test with custom validators
SERIALIZER_VALIDATED=$(mktemp)
cat > "$SERIALIZER_VALIDATED" << 'JSON'
{
  "id": 1,
  "name": "  John Doe  ",
  "email": "JOHN@EXAMPLE.COM",
  "bio": "Software developer"
}
JSON

echo "### Django-Bolt Serializer with Validators (POST /bench/serializer-validated)"
ab -k -c $C -n $N -p "$SERIALIZER_VALIDATED" -T 'application/json' http://$HOST:$PORT/bench/serializer-validated 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"
rm -f "$SERIALIZER_VALIDATED"

# Test users endpoint with raw msgspec
USER_BENCH=$(mktemp)
cat > "$USER_BENCH" << 'JSON'
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "bio": "Test bio"
}
JSON

echo "### Users msgspec Serializer (POST /users/bench/msgspec)"
USCODE=$(curl -s -o /dev/null -w '%{http_code}' -X POST -H 'Content-Type: application/json' --data-binary @"$USER_BENCH" http://$HOST:$PORT/users/bench/msgspec)
if [ "$USCODE" = "200" ]; then
  ab -k -c $C -n $N -p "$USER_BENCH" -T 'application/json' http://$HOST:$PORT/users/bench/msgspec 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests)"
else
  echo "Skipped: Users msgspec endpoint returned $USCODE" >&2
fi
rm -f "$USER_BENCH"

kill -TERM -$SERVER_PID 2>/dev/null || true
pkill -TERM -f "manage.py runbolt --host $HOST --port $PORT" 2>/dev/null || true


