#!/bin/bash
# Focused benchmark for parameter handling and form parsing
# Used to establish baseline before moving coercion to Rust

set -e

P=${P:-2}
WORKERS=${WORKERS:-2}
C=${C:-50}
N=${N:-10000}
HOST=${HOST:-127.0.0.1}
PORT=${PORT:-8000}

# Check if bombardier is available
BOMBARDIER_BIN=""
if command -v bombardier &> /dev/null; then
    BOMBARDIER_BIN="bombardier"
elif [ -f "$HOME/go/bin/bombardier" ]; then
    BOMBARDIER_BIN="$HOME/go/bin/bombardier"
elif [ -f "$HOME/.local/bin/bombardier" ]; then
    BOMBARDIER_BIN="$HOME/.local/bin/bombardier"
fi

if [ -z "$BOMBARDIER_BIN" ]; then
    echo "ERROR: bombardier not installed. Install with: go install github.com/codesenberg/bombardier@latest"
    exit 1
fi

echo "# Django-Bolt Parameter & Form Benchmark"
echo "Generated: $(date)"
echo "Config: $P processes x $WORKERS workers | C=$C N=$N"
echo ""

cd python/example
DJANGO_BOLT_WORKERS=$WORKERS setsid uv run python manage.py runbolt --host $HOST --port $PORT --processes $P >/dev/null 2>&1 &
SERVER_PID=$!
sleep 2

# Sanity check
CODE=$(curl -s -o /dev/null -w '%{http_code}' http://$HOST:$PORT/)
if [ "$CODE" != "200" ]; then
  echo "Expected 200 from / but got $CODE; aborting benchmark." >&2
  kill -TERM -$SERVER_PID 2>/dev/null || true
  pkill -TERM -f "manage.py runbolt --host $HOST --port $PORT" 2>/dev/null || true
  exit 1
fi

# Helper function to run benchmark and extract metrics
run_bench() {
    local name="$1"
    local url="$2"
    shift 2
    printf "### %s\n" "$name"
    $BOMBARDIER_BIN -c $C -n $N -l "$@" "$url" 2>&1 | grep -E "(Reqs/sec|Latency|50%|75%|90%|99%)"
    echo ""
}

run_bench_post() {
    local name="$1"
    local url="$2"
    local content_type="$3"
    local body_file="$4"
    printf "### %s\n" "$name"
    $BOMBARDIER_BIN -c $C -n $N -l -m POST -H "Content-Type: $content_type" -f "$body_file" "$url" 2>&1 | grep -E "(Reqs/sec|Latency|50%|75%|90%|99%)"
    echo ""
}

echo "## Parameter Extraction Performance"
echo ""

run_bench "Baseline - No Parameters (/)" "http://$HOST:$PORT/"

run_bench "Path Parameter - int (/items/12345)" "http://$HOST:$PORT/items/12345"

run_bench "Path + Query Parameters (/items/12345?q=hello)" "http://$HOST:$PORT/items/12345?q=hello"

run_bench "Typed Params - int/float/bool (/bench/params/typed/1?count=10&price=19.99&active=true)" \
    "http://$HOST:$PORT/bench/params/typed/1?count=10&price=19.99&active=true"

run_bench "Multi Query - 7 params (/bench/params/multi-query?page=1&limit=20&sort=name&order=desc&filter_active=true&min_price=10.0&max_price=500.0)" \
    "http://$HOST:$PORT/bench/params/multi-query?page=1&limit=20&sort=name&order=desc&filter_active=true&min_price=10.0&max_price=500.0"

run_bench "Header Extraction (/header)" "http://$HOST:$PORT/header" -H "x-test: benchmark-value"

run_bench "Cookie Extraction (/cookie)" "http://$HOST:$PORT/cookie" -H "Cookie: session=benchmark-session-id"

echo "## Form Parsing Performance"
echo ""

# URL-encoded form - existing endpoint (name, age int, email)
FORM_SIMPLE=$(mktemp)
echo "name=TestUser&age=25&email=test%40example.com" > "$FORM_SIMPLE"
run_bench_post "URL-Encoded Form - 3 fields (/form)" \
    "http://$HOST:$PORT/form" \
    "application/x-www-form-urlencoded" \
    "$FORM_SIMPLE"
rm -f "$FORM_SIMPLE"

# URL-encoded form with typed params (name, age int, score float, active bool)
FORM_TYPED=$(mktemp)
echo "name=TestUser&age=25&score=98.5&active=true" > "$FORM_TYPED"
run_bench_post "URL-Encoded Form - Typed int/float/bool (/bench/form/typed)" \
    "http://$HOST:$PORT/bench/form/typed" \
    "application/x-www-form-urlencoded" \
    "$FORM_TYPED"
rm -f "$FORM_TYPED"

# URL-encoded form with 10 fields
FORM_LARGE=$(mktemp)
echo "field1=value1&field2=value2&field3=value3&field4=value4&field5=value5&num1=100&num2=200&num3=3.14&flag1=true&flag2=false" > "$FORM_LARGE"
run_bench_post "URL-Encoded Form - 10 fields (/bench/form/large)" \
    "http://$HOST:$PORT/bench/form/large" \
    "application/x-www-form-urlencoded" \
    "$FORM_LARGE"
rm -f "$FORM_LARGE"

echo "## Multipart Form Parsing Performance"
echo ""

# Single file upload
UPLOAD_FILE=$(mktemp)
BOUNDARY="----BoltBenchmark$(date +%s)"
printf -- "--%s\r\n" "$BOUNDARY" > "$UPLOAD_FILE"
printf "Content-Disposition: form-data; name=\"file\"; filename=\"test.txt\"\r\n" >> "$UPLOAD_FILE"
printf "Content-Type: text/plain\r\n" >> "$UPLOAD_FILE"
printf "\r\n" >> "$UPLOAD_FILE"
printf "This is test file content for benchmarking\r\n" >> "$UPLOAD_FILE"
printf -- "--%s--\r\n" "$BOUNDARY" >> "$UPLOAD_FILE"

printf "### Multipart - Single File Upload (/upload)\n"
$BOMBARDIER_BIN -c $C -n $N -l -m POST -H "Content-Type: multipart/form-data; boundary=$BOUNDARY" -f "$UPLOAD_FILE" http://$HOST:$PORT/upload 2>&1 | grep -E "(Reqs/sec|Latency|50%|75%|90%|99%)"
echo ""
rm -f "$UPLOAD_FILE"

# Mixed form with file
MIXED_FILE=$(mktemp)
BOUNDARY="----BoltMixed$(date +%s)"
printf -- "--%s\r\n" "$BOUNDARY" > "$MIXED_FILE"
printf "Content-Disposition: form-data; name=\"title\"\r\n" >> "$MIXED_FILE"
printf "\r\n" >> "$MIXED_FILE"
printf "Test Title\r\n" >> "$MIXED_FILE"
printf -- "--%s\r\n" "$BOUNDARY" >> "$MIXED_FILE"
printf "Content-Disposition: form-data; name=\"description\"\r\n" >> "$MIXED_FILE"
printf "\r\n" >> "$MIXED_FILE"
printf "This is a test description for benchmarking\r\n" >> "$MIXED_FILE"
printf -- "--%s\r\n" "$BOUNDARY" >> "$MIXED_FILE"
printf "Content-Disposition: form-data; name=\"file\"; filename=\"attachment.txt\"\r\n" >> "$MIXED_FILE"
printf "Content-Type: text/plain\r\n" >> "$MIXED_FILE"
printf "\r\n" >> "$MIXED_FILE"
printf "File attachment content\r\n" >> "$MIXED_FILE"
printf -- "--%s--\r\n" "$BOUNDARY" >> "$MIXED_FILE"

printf "### Multipart - Mixed Form + File (/mixed-form)\n"
$BOMBARDIER_BIN -c $C -n $N -l -m POST -H "Content-Type: multipart/form-data; boundary=$BOUNDARY" -f "$MIXED_FILE" http://$HOST:$PORT/mixed-form 2>&1 | grep -E "(Reqs/sec|Latency|50%|75%|90%|99%)"
echo ""
rm -f "$MIXED_FILE"

# Multiple file upload
MULTI_FILE=$(mktemp)
BOUNDARY="----BoltMulti$(date +%s)"
printf -- "--%s\r\n" "$BOUNDARY" > "$MULTI_FILE"
printf "Content-Disposition: form-data; name=\"file\"; filename=\"test1.txt\"\r\n" >> "$MULTI_FILE"
printf "Content-Type: text/plain\r\n" >> "$MULTI_FILE"
printf "\r\n" >> "$MULTI_FILE"
printf "This is test file content 1\r\n" >> "$MULTI_FILE"
printf -- "--%s\r\n" "$BOUNDARY" >> "$MULTI_FILE"
printf "Content-Disposition: form-data; name=\"file\"; filename=\"test2.txt\"\r\n" >> "$MULTI_FILE"
printf "Content-Type: text/plain\r\n" >> "$MULTI_FILE"
printf "\r\n" >> "$MULTI_FILE"
printf "This is test file content 2\r\n" >> "$MULTI_FILE"
printf -- "--%s--\r\n" "$BOUNDARY" >> "$MULTI_FILE"

printf "### Multipart - Multiple Files (/upload)\n"
$BOMBARDIER_BIN -c $C -n $N -l -m POST -H "Content-Type: multipart/form-data; boundary=$BOUNDARY" -f "$MULTI_FILE" http://$HOST:$PORT/upload 2>&1 | grep -E "(Reqs/sec|Latency|50%|75%|90%|99%)"
echo ""
rm -f "$MULTI_FILE"

# Cleanup
kill -TERM -$SERVER_PID 2>/dev/null || true
pkill -TERM -f "manage.py runbolt --host $HOST --port $PORT" 2>/dev/null || true

echo "## Summary"
echo ""
echo "Use this benchmark before and after moving form parsing/coercion to Rust."
echo "Key metrics: Reqs/sec (higher=better), p50/p90/p99 latency (lower=better)"
