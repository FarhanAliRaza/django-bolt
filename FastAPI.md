# Django-Bolt Benchmark

Generated: Thu Sep 25 12:15:41 AM PKT 2025
Config: FastAPI with 4 uvicorn workers | C=100 N=10000 | Mode=fastapi

## Root Endpoint Performance

Starting FastAPI with uvicorn (workers=4)...
Failed requests: 0
Requests per second: 16439.99 [#/sec] (mean)
Time per request: 6.083 [ms] (mean)
Time per request: 0.061 [ms] (mean, across all concurrent requests)

## Response Type Endpoints

### Header Endpoint (/header)

Failed requests: 0
Requests per second: 20183.51 [#/sec] (mean)
Time per request: 4.955 [ms] (mean)
Time per request: 0.050 [ms] (mean, across all concurrent requests)

### Cookie Endpoint (/cookie)

Failed requests: 0
Requests per second: 19960.36 [#/sec] (mean)
Time per request: 5.010 [ms] (mean)
Time per request: 0.050 [ms] (mean, across all concurrent requests)

### Exception Endpoint (/exc)

Failed requests: 0
Requests per second: 18887.38 [#/sec] (mean)
Time per request: 5.295 [ms] (mean)
Time per request: 0.053 [ms] (mean, across all concurrent requests)

### HTML Response (/html)

Failed requests: 0
Requests per second: 19304.53 [#/sec] (mean)
Time per request: 5.180 [ms] (mean)
Time per request: 0.052 [ms] (mean, across all concurrent requests)

### Redirect Response (/redirect)

Failed requests: 0
Requests per second: 18010.00 [#/sec] (mean)
Time per request: 5.552 [ms] (mean)
Time per request: 0.056 [ms] (mean, across all concurrent requests)

### File Static via FileResponse (/file-static)

Failed requests: 0
Requests per second: 8013.58 [#/sec] (mean)
Time per request: 12.479 [ms] (mean)
Time per request: 0.125 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance

### Streaming Plain Text (/stream)

Total: 0.6133 secs
Slowest: 0.0423 secs
Fastest: 0.0003 secs
Average: 0.0058 secs
Requests/sec: 16305.9260
Status code distribution:

### Server-Sent Events (/sse)

Total: 0.3853 secs
Slowest: 0.0315 secs
Fastest: 0.0002 secs
Average: 0.0036 secs
Requests/sec: 25955.6001
Status code distribution:

### Server-Sent Events (async) (/sse-async)

Total: 0.2113 secs
Slowest: 0.0147 secs
Fastest: 0.0002 secs
Average: 0.0020 secs
Requests/sec: 47317.3954
Status code distribution:

### OpenAI Chat Completions (stream) (/v1/chat/completions)

Total: 1.0134 secs
Slowest: 0.0722 secs
Fastest: 0.0004 secs
Average: 0.0097 secs
Requests/sec: 9867.5608
Status code distribution:

### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)

Total: 0.2140 secs
Slowest: 0.0134 secs
Fastest: 0.0001 secs
Average: 0.0020 secs
Requests/sec: 46723.5278
Status code distribution:

## Items GET Performance (/items/1?q=hello)

Failed requests: 0
Requests per second: 20106.48 [#/sec] (mean)
Time per request: 4.974 [ms] (mean)
Time per request: 0.050 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)

Failed requests: 0
Requests per second: 20226.33 [#/sec] (mean)
Time per request: 4.944 [ms] (mean)
Time per request: 0.049 [ms] (mean, across all concurrent requests)

## ORM Performance

### Users Full10 (/users/full10)

Failed requests: 0
Requests per second: 2951.94 [#/sec] (mean)
Time per request: 33.876 [ms] (mean)
Time per request: 0.339 [ms] (mean, across all concurrent requests)

### Users Mini10 (/users/mini10)

Failed requests: 0
Requests per second: 3823.56 [#/sec] (mean)
Time per request: 26.154 [ms] (mean)
Time per request: 0.262 [ms] (mean, across all concurrent requests)

## Form and File Upload Performance

### Form Data (POST /form)

### File Upload (POST /upload)

### Mixed Form with Files (POST /mixed-form)

## Django Ninja-style Benchmarks

### JSON Parse/Validate (POST /bench/parse)

Failed requests: 0
Requests per second: 18842.97 [#/sec] (mean)
Time per request: 5.307 [ms] (mean)
Time per request: 0.053 [ms] (mean, across all concurrent requests)
