# Django-Bolt Benchmark

Generated: Mon Oct 13 09:27:30 PM PKT 2025
Config: 8 processes | C=100 N=10000
uv run uvicorn main:app --host 127.0.0.1 --port 8000 --workers 12 --log-level critical --no-access-log --loop uvloop --http httptools

## Root Endpoint Performance

./benchmark.sh: line 23: cd: python/examples/testproject: No such file or directory
Failed requests: 0
Requests per second: 14181.56 [#/sec] (mean)
Time per request: 7.051 [ms] (mean)
Time per request: 0.071 [ms] (mean, across all concurrent requests)

## Response Type Endpoints

### Header Endpoint (/header)

Failed requests: 0
Requests per second: 14352.68 [#/sec] (mean)
Time per request: 6.967 [ms] (mean)
Time per request: 0.070 [ms] (mean, across all concurrent requests)

### Cookie Endpoint (/cookie)

Failed requests: 0
Requests per second: 14261.98 [#/sec] (mean)
Time per request: 7.012 [ms] (mean)
Time per request: 0.070 [ms] (mean, across all concurrent requests)

### Exception Endpoint (/exc)

Failed requests: 0
Requests per second: 14358.57 [#/sec] (mean)
Time per request: 6.964 [ms] (mean)
Time per request: 0.070 [ms] (mean, across all concurrent requests)

### HTML Response (/html)

Failed requests: 0
Requests per second: 14625.72 [#/sec] (mean)
Time per request: 6.837 [ms] (mean)
Time per request: 0.068 [ms] (mean, across all concurrent requests)

### Redirect Response (/redirect)

Failed requests: 0
Requests per second: 14374.67 [#/sec] (mean)
Time per request: 6.957 [ms] (mean)
Time per request: 0.070 [ms] (mean, across all concurrent requests)

### File Static via FileResponse (/file-static)

Failed requests: 0
Requests per second: 9822.04 [#/sec] (mean)
Time per request: 10.181 [ms] (mean)
Time per request: 0.102 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance

### Streaming Plain Text (/stream)

Total: 0.4076 secs
Slowest: 0.0349 secs
Fastest: 0.0003 secs
Average: 0.0039 secs
Requests/sec: 24536.7488
Status code distribution:

### Server-Sent Events (/sse)

Total: 0.2955 secs
Slowest: 0.0419 secs
Fastest: 0.0002 secs
Average: 0.0027 secs
Requests/sec: 33837.2150
Status code distribution:

### Server-Sent Events (async) (/sse-async)

Total: 0.1775 secs
Slowest: 0.0100 secs
Fastest: 0.0001 secs
Average: 0.0016 secs
Requests/sec: 56330.5751
Status code distribution:

### OpenAI Chat Completions (stream) (/v1/chat/completions)

Total: 0.6498 secs
Slowest: 0.0499 secs
Fastest: 0.0004 secs
Average: 0.0059 secs
Requests/sec: 15388.5654
Status code distribution:

### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)

Total: 0.1804 secs
Slowest: 0.0105 secs
Fastest: 0.0001 secs
Average: 0.0017 secs
Requests/sec: 55423.3103
Status code distribution:

## Items GET Performance (/items/1?q=hello)

Failed requests: 0
Requests per second: 13823.76 [#/sec] (mean)
Time per request: 7.234 [ms] (mean)
Time per request: 0.072 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)

Failed requests: 0
Requests per second: 13561.57 [#/sec] (mean)
Time per request: 7.374 [ms] (mean)
Time per request: 0.074 [ms] (mean, across all concurrent requests)

## ORM Performance

### Users Full10 (/users/full10)

Failed requests: 0
Requests per second: 6044.76 [#/sec] (mean)
Time per request: 16.543 [ms] (mean)
Time per request: 0.165 [ms] (mean, across all concurrent requests)

### Users Mini10 (/users/mini10)

Failed requests: 0
Requests per second: 6566.47 [#/sec] (mean)
Time per request: 15.229 [ms] (mean)
Time per request: 0.152 [ms] (mean, across all concurrent requests)

## Form and File Upload Performance

### Form Data (POST /form)

Failed requests: 0
Requests per second: 13575.24 [#/sec] (mean)
Time per request: 7.366 [ms] (mean)
Time per request: 0.074 [ms] (mean, across all concurrent requests)

### File Upload (POST /upload)

Failed requests: 0
Requests per second: 11881.10 [#/sec] (mean)
Time per request: 8.417 [ms] (mean)
Time per request: 0.084 [ms] (mean, across all concurrent requests)

### Mixed Form with Files (POST /mixed-form)

Failed requests: 0
Requests per second: 11376.59 [#/sec] (mean)
Time per request: 8.790 [ms] (mean)
Time per request: 0.088 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks

### JSON Parse/Validate (POST /bench/parse)

Failed requests: 0
Requests per second: 14164.01 [#/sec] (mean)
Time per request: 7.060 [ms] (mean)
Time per request: 0.071 [ms] (mean, across all concurrent requests)
