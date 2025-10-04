# FAST API Benchmark

Generated: Mon Sep 22 12:25:01 AM PKT 2025
Config: 8 processes × 1 uvicorn | C=100 N=10000
uvicorn main:app --host 127.0.0.1 --port 8000 --workers 8 --log-level error

## Root Endpoint Performance

Failed requests: 0
Requests per second: 16265.66 [#/sec] (mean)
Time per request: 6.148 [ms] (mean)
Time per request: 0.061 [ms] (mean, across all concurrent requests)

## Response Type Endpoints

### Header Endpoint (/header)

Failed requests: 0
Requests per second: 16590.24 [#/sec] (mean)
Time per request: 6.028 [ms] (mean)
Time per request: 0.060 [ms] (mean, across all concurrent requests)

### Cookie Endpoint (/cookie)

Failed requests: 0
Requests per second: 16199.34 [#/sec] (mean)
Time per request: 6.173 [ms] (mean)
Time per request: 0.062 [ms] (mean, across all concurrent requests)

### Exception Endpoint (/exc)

Failed requests: 0
Requests per second: 16671.61 [#/sec] (mean)
Time per request: 5.998 [ms] (mean)
Time per request: 0.060 [ms] (mean, across all concurrent requests)

### HTML Response (/html)

Failed requests: 0
Requests per second: 15898.55 [#/sec] (mean)
Time per request: 6.290 [ms] (mean)
Time per request: 0.063 [ms] (mean, across all concurrent requests)

### Redirect Response (/redirect)

Failed requests: 0
Requests per second: 15259.95 [#/sec] (mean)
Time per request: 6.553 [ms] (mean)
Time per request: 0.066 [ms] (mean, across all concurrent requests)

### File Static via FileResponse (/file-static)

Failed requests: 0
Requests per second: 10308.12 [#/sec] (mean)
Time per request: 9.701 [ms] (mean)
Time per request: 0.097 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance

### Streaming Plain Text (/stream)

Total: 0.4451 secs
Slowest: 0.0431 secs
Fastest: 0.0003 secs
Average: 0.0042 secs
Requests/sec: 22465.1548
Status code distribution:

### Server-Sent Events (/sse)

Total: 0.2904 secs
Slowest: 0.0548 secs
Fastest: 0.0002 secs
Average: 0.0026 secs
Requests/sec: 34430.8564
Status code distribution:

### Server-Sent Events (async) (/sse-async)

Total: 0.1924 secs
Slowest: 0.0110 secs
Fastest: 0.0001 secs
Average: 0.0018 secs
Requests/sec: 51983.1018
Status code distribution:

### OpenAI Chat Completions (stream) (/v1/chat/completions)

Total: 0.7590 secs
Slowest: 0.0596 secs
Fastest: 0.0004 secs
Average: 0.0069 secs
Requests/sec: 13175.5236
Status code distribution:

### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)

Total: 0.2095 secs
Slowest: 0.0298 secs
Fastest: 0.0001 secs
Average: 0.0020 secs
Requests/sec: 47741.8556
Status code distribution:

## Items GET Performance (/items/1?q=hello)

Failed requests: 0
Requests per second: 16176.96 [#/sec] (mean)
Time per request: 6.182 [ms] (mean)
Time per request: 0.062 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)

Failed requests: 0
Requests per second: 16146.85 [#/sec] (mean)
Time per request: 6.193 [ms] (mean)
Time per request: 0.062 [ms] (mean, across all concurrent requests)

## ORM Performance

### Users Full10 (/users/full10)

Failed requests: 0
Requests per second: 6304.65 [#/sec] (mean)
Time per request: 15.861 [ms] (mean)
Time per request: 0.159 [ms] (mean, across all concurrent requests)

### Users Mini10 (/users/mini10)

Failed requests: 0
Requests per second: 7126.93 [#/sec] (mean)
Time per request: 14.031 [ms] (mean)
Time per request: 0.140 [ms] (mean, across all concurrent requests)

## Form and File Upload Performance

### Form Data (POST /form)

Failed requests: 0
Requests per second: 16136.71 [#/sec] (mean)
Time per request: 6.197 [ms] (mean)
Time per request: 0.062 [ms] (mean, across all concurrent requests)

### File Upload (POST /upload)

Failed requests: 0
Requests per second: 11953.29 [#/sec] (mean)
Time per request: 8.366 [ms] (mean)
Time per request: 0.084 [ms] (mean, across all concurrent requests)

### Mixed Form with Files (POST /mixed-form)

Failed requests: 0
Requests per second: 12873.24 [#/sec] (mean)
Time per request: 7.768 [ms] (mean)
Time per request: 0.078 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks

### JSON Parse/Validate (POST /bench/parse)

Failed requests: 0
Requests per second: 16236.59 [#/sec] (mean)
Time per request: 6.159 [ms] (mean)
Time per request: 0.062 [ms] (mean, across all concurrent requests)
