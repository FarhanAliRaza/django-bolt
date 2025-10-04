# Django-Bolt Benchmark

Generated: Sat Oct 4 02:00:13 PM PKT 2025
Config: 4 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance

Failed requests: 0
Requests per second: 46949.46 [#/sec] (mean)
Time per request: 2.130 [ms] (mean)
Time per request: 0.021 [ms] (mean, across all concurrent requests)

## Response Type Endpoints

### Header Endpoint (/header)

Failed requests: 0
Requests per second: 46217.56 [#/sec] (mean)
Time per request: 2.164 [ms] (mean)
Time per request: 0.022 [ms] (mean, across all concurrent requests)

### Cookie Endpoint (/cookie)

Failed requests: 0
Requests per second: 46004.30 [#/sec] (mean)
Time per request: 2.174 [ms] (mean)
Time per request: 0.022 [ms] (mean, across all concurrent requests)

### Exception Endpoint (/exc)

Failed requests: 0
Requests per second: 45491.35 [#/sec] (mean)
Time per request: 2.198 [ms] (mean)
Time per request: 0.022 [ms] (mean, across all concurrent requests)

### HTML Response (/html)

Failed requests: 0
Requests per second: 46761.53 [#/sec] (mean)
Time per request: 2.139 [ms] (mean)
Time per request: 0.021 [ms] (mean, across all concurrent requests)

### Redirect Response (/redirect)

Failed requests: 0
Requests per second: 47723.81 [#/sec] (mean)
Time per request: 2.095 [ms] (mean)
Time per request: 0.021 [ms] (mean, across all concurrent requests)

### File Static via FileResponse (/file-static)

Failed requests: 0
Requests per second: 2432.76 [#/sec] (mean)
Time per request: 41.106 [ms] (mean)
Time per request: 0.411 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance

### Streaming Plain Text (/stream)

Total: 0.3586 secs
Slowest: 0.0100 secs
Fastest: 0.0001 secs
Average: 0.0034 secs
Requests/sec: 27889.7095
Status code distribution:

### Server-Sent Events (/sse)

Total: 0.3162 secs
Slowest: 0.0089 secs
Fastest: 0.0001 secs
Average: 0.0030 secs
Requests/sec: 31630.0021
Status code distribution:

### Server-Sent Events (async) (/sse-async)

Total: 0.6994 secs
Slowest: 0.0145 secs
Fastest: 0.0003 secs
Average: 0.0067 secs
Requests/sec: 14298.5509
Status code distribution:

### OpenAI Chat Completions (stream) (/v1/chat/completions)

Total: 1.0906 secs
Slowest: 0.0240 secs
Fastest: 0.0003 secs
Average: 0.0100 secs
Requests/sec: 9169.6317
Status code distribution:

### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)

Total: 1.5020 secs
Slowest: 0.0337 secs
Fastest: 0.0005 secs
Average: 0.0145 secs
Requests/sec: 6657.9644
Status code distribution:

## Items GET Performance (/items/1?q=hello)

Failed requests: 0
Requests per second: 39293.66 [#/sec] (mean)
Time per request: 2.545 [ms] (mean)
Time per request: 0.025 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)

Failed requests: 0
Requests per second: 40703.69 [#/sec] (mean)
Time per request: 2.457 [ms] (mean)
Time per request: 0.025 [ms] (mean, across all concurrent requests)

## ORM Performance

### Users Full10 (/users/full10)

Failed requests: 0
Requests per second: 6959.61 [#/sec] (mean)
Time per request: 14.369 [ms] (mean)
Time per request: 0.144 [ms] (mean, across all concurrent requests)

### Users Mini10 (/users/mini10)

Failed requests: 0
Requests per second: 8147.08 [#/sec] (mean)
Time per request: 12.274 [ms] (mean)
Time per request: 0.123 [ms] (mean, across all concurrent requests)

## Form and File Upload Performance

### Form Data (POST /form)

Failed requests: 0
Requests per second: 37749.24 [#/sec] (mean)
Time per request: 2.649 [ms] (mean)
Time per request: 0.026 [ms] (mean, across all concurrent requests)

### File Upload (POST /upload)

Failed requests: 0
Requests per second: 45194.88 [#/sec] (mean)
Time per request: 2.213 [ms] (mean)
Time per request: 0.022 [ms] (mean, across all concurrent requests)

### Mixed Form with Files (POST /mixed-form)

Failed requests: 0
Requests per second: 44553.75 [#/sec] (mean)
Time per request: 2.244 [ms] (mean)
Time per request: 0.022 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks

### JSON Parse/Validate (POST /bench/parse)

Failed requests: 0
Requests per second: 44066.06 [#/sec] (mean)
Time per request: 2.269 [ms] (mean)
Time per request: 0.023 [ms] (mean, across all concurrent requests)
