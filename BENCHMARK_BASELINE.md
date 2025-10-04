# Django-Bolt Benchmark

Generated: Sat Oct 4 01:01:40 PM PKT 2025
Config: 4 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance

Failed requests: 0
Requests per second: 45917.69 [#/sec] (mean)
Time per request: 2.178 [ms] (mean)
Time per request: 0.022 [ms] (mean, across all concurrent requests)

## Response Type Endpoints

### Header Endpoint (/header)

Failed requests: 0
Requests per second: 46075.94 [#/sec] (mean)
Time per request: 2.170 [ms] (mean)
Time per request: 0.022 [ms] (mean, across all concurrent requests)

### Cookie Endpoint (/cookie)

Failed requests: 0
Requests per second: 46144.83 [#/sec] (mean)
Time per request: 2.167 [ms] (mean)
Time per request: 0.022 [ms] (mean, across all concurrent requests)

### Exception Endpoint (/exc)

Failed requests: 0
Requests per second: 47286.69 [#/sec] (mean)
Time per request: 2.115 [ms] (mean)
Time per request: 0.021 [ms] (mean, across all concurrent requests)

### HTML Response (/html)

Failed requests: 0
Requests per second: 47689.90 [#/sec] (mean)
Time per request: 2.097 [ms] (mean)
Time per request: 0.021 [ms] (mean, across all concurrent requests)

### Redirect Response (/redirect)

Failed requests: 0
Requests per second: 50878.16 [#/sec] (mean)
Time per request: 1.965 [ms] (mean)
Time per request: 0.020 [ms] (mean, across all concurrent requests)

### File Static via FileResponse (/file-static)

Failed requests: 0
Requests per second: 2428.45 [#/sec] (mean)
Time per request: 41.179 [ms] (mean)
Time per request: 0.412 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance

### Streaming Plain Text (/stream)

Total: 0.3517 secs
Slowest: 0.0092 secs
Fastest: 0.0001 secs
Average: 0.0034 secs
Requests/sec: 28429.6809
Status code distribution:

### Server-Sent Events (/sse)

Total: 0.3252 secs
Slowest: 0.0189 secs
Fastest: 0.0002 secs
Average: 0.0031 secs
Requests/sec: 30747.1899
Status code distribution:

### Server-Sent Events (async) (/sse-async)

Total: 0.7060 secs
Slowest: 0.0267 secs
Fastest: 0.0003 secs
Average: 0.0067 secs
Requests/sec: 14163.8725
Status code distribution:

### OpenAI Chat Completions (stream) (/v1/chat/completions)

Total: 1.1975 secs
Slowest: 0.0329 secs
Fastest: 0.0004 secs
Average: 0.0114 secs
Requests/sec: 8350.5286
Status code distribution:

### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)

Total: 1.5702 secs
Slowest: 0.0397 secs
Fastest: 0.0005 secs
Average: 0.0145 secs
Requests/sec: 6368.7259
Status code distribution:

## Items GET Performance (/items/1?q=hello)

Failed requests: 0
Requests per second: 39141.55 [#/sec] (mean)
Time per request: 2.555 [ms] (mean)
Time per request: 0.026 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)

Failed requests: 0
Requests per second: 40922.22 [#/sec] (mean)
Time per request: 2.444 [ms] (mean)
Time per request: 0.024 [ms] (mean, across all concurrent requests)

## ORM Performance

### Users Full10 (/users/full10)

Failed requests: 0
Requests per second: 6840.39 [#/sec] (mean)
Time per request: 14.619 [ms] (mean)
Time per request: 0.146 [ms] (mean, across all concurrent requests)

### Users Mini10 (/users/mini10)

Failed requests: 0
Requests per second: 8310.72 [#/sec] (mean)
Time per request: 12.033 [ms] (mean)
Time per request: 0.120 [ms] (mean, across all concurrent requests)

## Form and File Upload Performance

### Form Data (POST /form)

Failed requests: 0
Requests per second: 37078.51 [#/sec] (mean)
Time per request: 2.697 [ms] (mean)
Time per request: 0.027 [ms] (mean, across all concurrent requests)

### File Upload (POST /upload)

Failed requests: 0
Requests per second: 44419.17 [#/sec] (mean)
Time per request: 2.251 [ms] (mean)
Time per request: 0.023 [ms] (mean, across all concurrent requests)

### Mixed Form with Files (POST /mixed-form)

Failed requests: 0
Requests per second: 43795.11 [#/sec] (mean)
Time per request: 2.283 [ms] (mean)
Time per request: 0.023 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks

### JSON Parse/Validate (POST /bench/parse)

Failed requests: 0
Requests per second: 46819.99 [#/sec] (mean)
Time per request: 2.136 [ms] (mean)
Time per request: 0.021 [ms] (mean, across all concurrent requests)
