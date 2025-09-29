# Django-Bolt Benchmark

Generated: Mon Sep 22 12:23:22 AM PKT 2025
Config: 4 processes × 1 workers | C=50 N=10000

## Root Endpoint Performance

Failed requests: 0
Requests per second: 66517.67 [#/sec] (mean)
Time per request: 0.752 [ms] (mean)
Time per request: 0.015 [ms] (mean, across all concurrent requests)

## Response Type Endpoints

### Header Endpoint (/header)

Failed requests: 0
Requests per second: 68204.45 [#/sec] (mean)
Time per request: 0.733 [ms] (mean)
Time per request: 0.015 [ms] (mean, across all concurrent requests)

### Cookie Endpoint (/cookie)

Failed requests: 0
Requests per second: 66518.99 [#/sec] (mean)
Time per request: 0.752 [ms] (mean)
Time per request: 0.015 [ms] (mean, across all concurrent requests)

### Exception Endpoint (/exc)

Failed requests: 0
Requests per second: 65005.56 [#/sec] (mean)
Time per request: 0.769 [ms] (mean)
Time per request: 0.015 [ms] (mean, across all concurrent requests)

### HTML Response (/html)

Failed requests: 0
Requests per second: 67780.99 [#/sec] (mean)
Time per request: 0.738 [ms] (mean)
Time per request: 0.015 [ms] (mean, across all concurrent requests)

### Redirect Response (/redirect)

Failed requests: 0
Requests per second: 66471.24 [#/sec] (mean)
Time per request: 0.752 [ms] (mean)
Time per request: 0.015 [ms] (mean, across all concurrent requests)

### File Static via FileResponse (/file-static)

Failed requests: 0
Requests per second: 1218.37 [#/sec] (mean)
Time per request: 41.038 [ms] (mean)
Time per request: 0.821 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance

### Streaming Plain Text (/stream)

Total: 8.2343 secs
Slowest: 0.0613 secs
Fastest: 0.0006 secs
Average: 0.0402 secs
Requests/sec: 1214.4377
Status code distribution:

### Server-Sent Events (/sse)

Total: 8.3337 secs
Slowest: 0.0452 secs
Fastest: 0.0002 secs
Average: 0.0412 secs
Requests/sec: 1199.9479
Status code distribution:

### Server-Sent Events (async) (/sse-async)

Total: 8.2886 secs
Slowest: 0.0471 secs
Fastest: 0.0022 secs
Average: 0.0413 secs
Requests/sec: 1206.4738
Status code distribution:

### OpenAI Chat Completions (stream) (/v1/chat/completions)

Total: 8.3095 secs
Slowest: 0.0530 secs
Fastest: 0.0054 secs
Average: 0.0414 secs
Requests/sec: 1203.4363
Status code distribution:

### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)

Total: 10.4306 secs
Slowest: 0.0783 secs
Fastest: 0.0047 secs
Average: 0.0503 secs
Requests/sec: 958.7132
Status code distribution:

### OpenAI Chat Completions (non-stream) (/v1/chat/completions)

Total: 0.2693 secs
Slowest: 0.0066 secs
Fastest: 0.0001 secs
Average: 0.0013 secs
Requests/sec: 37140.0696
Status code distribution:

## Items GET Performance (/items/1?q=hello)

Failed requests: 0
Requests per second: 55753.48 [#/sec] (mean)
Time per request: 0.897 [ms] (mean)
Time per request: 0.018 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)

Failed requests: 0
Requests per second: 53388.29 [#/sec] (mean)
Time per request: 0.937 [ms] (mean)
Time per request: 0.019 [ms] (mean, across all concurrent requests)

## ORM Performance

### Users Full10 (/users/full10)

Failed requests: 0
Requests per second: 7288.12 [#/sec] (mean)
Time per request: 6.860 [ms] (mean)
Time per request: 0.137 [ms] (mean, across all concurrent requests)
\n### Users Mini10 (/users/mini10)
Failed requests: 0
Requests per second: 8725.05 [#/sec] (mean)
Time per request: 5.731 [ms] (mean)
Time per request: 0.115 [ms] (mean, across all concurrent requests)

## Form and File Upload Performance

\n### Form Data (POST /form)
Failed requests: 0
Requests per second: 48388.66 [#/sec] (mean)
Time per request: 1.033 [ms] (mean)
Time per request: 0.021 [ms] (mean, across all concurrent requests)
\n### File Upload (POST /upload)
Failed requests: 0
Requests per second: 55896.52 [#/sec] (mean)
Time per request: 0.895 [ms] (mean)
Time per request: 0.018 [ms] (mean, across all concurrent requests)
\n### Mixed Form with Files (POST /mixed-form)
Failed requests: 0
Requests per second: 56939.83 [#/sec] (mean)
Time per request: 0.878 [ms] (mean)
Time per request: 0.018 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks

### JSON Parse/Validate (POST /bench/parse)

Failed requests: 0
Requests per second: 57971.69 [#/sec] (mean)
Time per request: 0.862 [ms] (mean)
Time per request: 0.017 [ms] (mean, across all concurrent requests)
