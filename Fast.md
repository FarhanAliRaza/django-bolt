# Django-Bolt Benchmark

Generated: Mon Sep 22 12:25:01 AM PKT 2025
Config: 4 processes × 1 workers | C=50 N=10000

## Root Endpoint Performance

Failed requests: 0
Requests per second: 15468.02 [#/sec] (mean)
Time per request: 3.232 [ms] (mean)
Time per request: 0.065 [ms] (mean, across all concurrent requests)

## Response Type Endpoints

### Header Endpoint (/header)

Failed requests: 0
Requests per second: 15962.23 [#/sec] (mean)
Time per request: 3.132 [ms] (mean)
Time per request: 0.063 [ms] (mean, across all concurrent requests)

### Cookie Endpoint (/cookie)

Failed requests: 0
Requests per second: 12949.28 [#/sec] (mean)
Time per request: 3.861 [ms] (mean)
Time per request: 0.077 [ms] (mean, across all concurrent requests)

### Exception Endpoint (/exc)

Failed requests: 0
Requests per second: 14392.15 [#/sec] (mean)
Time per request: 3.474 [ms] (mean)
Time per request: 0.069 [ms] (mean, across all concurrent requests)

### HTML Response (/html)

Failed requests: 0
Requests per second: 15075.68 [#/sec] (mean)
Time per request: 3.317 [ms] (mean)
Time per request: 0.066 [ms] (mean, across all concurrent requests)

### Redirect Response (/redirect)

Failed requests: 0
Requests per second: 15609.15 [#/sec] (mean)
Time per request: 3.203 [ms] (mean)
Time per request: 0.064 [ms] (mean, across all concurrent requests)

### File Static via FileResponse (/file-static)

Failed requests: 0
Requests per second: 6716.04 [#/sec] (mean)
Time per request: 7.445 [ms] (mean)
Time per request: 0.149 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance

### Streaming Plain Text (/stream)

Total: 0.8003 secs
Slowest: 0.0117 secs
Fastest: 0.0004 secs
Average: 0.0039 secs
Requests/sec: 12494.5736
Status code distribution:

### Server-Sent Events (/sse)

Total: 0.5946 secs
Slowest: 0.0157 secs
Fastest: 0.0002 secs
Average: 0.0029 secs
Requests/sec: 16817.2355
Status code distribution:

### Server-Sent Events (async) (/sse-async)

Total: 0.3734 secs
Slowest: 0.0080 secs
Fastest: 0.0002 secs
Average: 0.0018 secs
Requests/sec: 26777.3735
Status code distribution:

### OpenAI Chat Completions (stream) (/v1/chat/completions)

Total: 1.2429 secs
Slowest: 0.0146 secs
Fastest: 0.0005 secs
Average: 0.0061 secs
Requests/sec: 8045.6558
Status code distribution:

### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)

Total: 0.3817 secs
Slowest: 0.0089 secs
Fastest: 0.0002 secs
Average: 0.0018 secs
Requests/sec: 26200.2379
Status code distribution:

### OpenAI Chat Completions (non-stream) (/v1/chat/completions)

Total: 0.5565 secs
Slowest: 0.0076 secs
Fastest: 0.0002 secs
Average: 0.0027 secs
Requests/sec: 17969.1236
Status code distribution:

## Items GET Performance (/items/1?q=hello)

Failed requests: 0
Requests per second: 14686.53 [#/sec] (mean)
Time per request: 3.404 [ms] (mean)
Time per request: 0.068 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)

Failed requests: 0
Requests per second: 12876.00 [#/sec] (mean)
Time per request: 3.883 [ms] (mean)
Time per request: 0.078 [ms] (mean, across all concurrent requests)

## ORM Performance
