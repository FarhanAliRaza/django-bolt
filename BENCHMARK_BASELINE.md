# Django-Bolt Benchmark

Generated: Fri Oct 24 05:06:01 PM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance

Failed requests: 0
Requests per second: 86930.82 [#/sec] (mean)
Time per request: 1.150 [ms] (mean)
Time per request: 0.012 [ms] (mean, across all concurrent requests)

## 10kb JSON Response Performance

### 10kb JSON (/10k-json)

Failed requests: 0
Requests per second: 72556.30 [#/sec] (mean)
Time per request: 1.378 [ms] (mean)
Time per request: 0.014 [ms] (mean, across all concurrent requests)

## Response Type Endpoints

### Header Endpoint (/header)

Failed requests: 0
Requests per second: 86276.81 [#/sec] (mean)
Time per request: 1.159 [ms] (mean)
Time per request: 0.012 [ms] (mean, across all concurrent requests)

### Cookie Endpoint (/cookie)

Failed requests: 0
Requests per second: 82339.09 [#/sec] (mean)
Time per request: 1.214 [ms] (mean)
Time per request: 0.012 [ms] (mean, across all concurrent requests)

### Exception Endpoint (/exc)

Failed requests: 0
Requests per second: 82468.11 [#/sec] (mean)
Time per request: 1.213 [ms] (mean)
Time per request: 0.012 [ms] (mean, across all concurrent requests)

### HTML Response (/html)

Failed requests: 0
Requests per second: 87550.34 [#/sec] (mean)
Time per request: 1.142 [ms] (mean)
Time per request: 0.011 [ms] (mean, across all concurrent requests)

### Redirect Response (/redirect)

Failed requests: 0
Requests per second: 88849.40 [#/sec] (mean)
Time per request: 1.125 [ms] (mean)
Time per request: 0.011 [ms] (mean, across all concurrent requests)

### File Static via FileResponse (/file-static)

Failed requests: 0
Requests per second: 34060.99 [#/sec] (mean)
Time per request: 2.936 [ms] (mean)
Time per request: 0.029 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance

### Streaming Plain Text (/stream)

Total: 0.1960 secs
Slowest: 0.0074 secs
Fastest: 0.0002 secs
Average: 0.0019 secs
Requests/sec: 51013.7847
Status code distribution:

### Server-Sent Events (/sse)

Total: 0.1768 secs
Slowest: 0.0116 secs
Fastest: 0.0001 secs
Average: 0.0017 secs
Requests/sec: 56546.9259
Status code distribution:

### Server-Sent Events (async) (/sse-async)

Total: 0.3462 secs
Slowest: 0.0128 secs
Fastest: 0.0003 secs
Average: 0.0033 secs
Requests/sec: 28885.0211
Status code distribution:

### OpenAI Chat Completions (stream) (/v1/chat/completions)

Total: 0.6017 secs
Slowest: 0.0201 secs
Fastest: 0.0004 secs
Average: 0.0058 secs
Requests/sec: 16618.2058
Status code distribution:

### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)

Total: 0.7706 secs
Slowest: 0.0249 secs
Fastest: 0.0005 secs
Average: 0.0074 secs
Requests/sec: 12977.0646
Status code distribution:

## Items GET Performance (/items/1?q=hello)

Failed requests: 0
Requests per second: 82556.61 [#/sec] (mean)
Time per request: 1.211 [ms] (mean)
Time per request: 0.012 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)

Failed requests: 0
Requests per second: 75547.53 [#/sec] (mean)
Time per request: 1.324 [ms] (mean)
Time per request: 0.013 [ms] (mean, across all concurrent requests)

## ORM Performance

### Users Full10 (/users/full10)

Failed requests: 0
Requests per second: 14055.35 [#/sec] (mean)
Time per request: 7.115 [ms] (mean)
Time per request: 0.071 [ms] (mean, across all concurrent requests)

### Users Mini10 (/users/mini10)

Failed requests: 0
Requests per second: 15448.43 [#/sec] (mean)
Time per request: 6.473 [ms] (mean)
Time per request: 0.065 [ms] (mean, across all concurrent requests)

## Class-Based Views (CBV) Performance

### Simple APIView GET (/cbv-simple)

Failed requests: 0
Requests per second: 87359.90 [#/sec] (mean)
Time per request: 1.145 [ms] (mean)
Time per request: 0.011 [ms] (mean, across all concurrent requests)

### Simple APIView POST (/cbv-simple)

Failed requests: 0
Requests per second: 81417.31 [#/sec] (mean)
Time per request: 1.228 [ms] (mean)
Time per request: 0.012 [ms] (mean, across all concurrent requests)

### Items100 ViewSet GET (/cbv-items100)

Failed requests: 0
Requests per second: 60996.81 [#/sec] (mean)
Time per request: 1.639 [ms] (mean)
Time per request: 0.016 [ms] (mean, across all concurrent requests)

## CBV Items - Basic Operations

### CBV Items GET (Retrieve) (/cbv-items/1)

Failed requests: 0
Requests per second: 83250.08 [#/sec] (mean)
Time per request: 1.201 [ms] (mean)
Time per request: 0.012 [ms] (mean, across all concurrent requests)

### CBV Items PUT (Update) (/cbv-items/1)

Failed requests: 0
Requests per second: 78231.35 [#/sec] (mean)
Time per request: 1.278 [ms] (mean)
Time per request: 0.013 [ms] (mean, across all concurrent requests)

## CBV Additional Benchmarks

### CBV Bench Parse (POST /cbv-bench-parse)

Failed requests: 0
Requests per second: 76924.85 [#/sec] (mean)
Time per request: 1.300 [ms] (mean)
Time per request: 0.013 [ms] (mean, across all concurrent requests)

### CBV Response Types (/cbv-response)

Failed requests: 0
Requests per second: 85114.35 [#/sec] (mean)
Time per request: 1.175 [ms] (mean)
Time per request: 0.012 [ms] (mean, across all concurrent requests)

### CBV Streaming Plain Text (/cbv-stream)

Total: 0.3512 secs
Slowest: 0.0184 secs
Fastest: 0.0002 secs
Average: 0.0033 secs
Requests/sec: 28476.3706
Status code distribution:

### CBV Server-Sent Events (/cbv-sse)

Total: 0.3457 secs
Slowest: 0.0143 secs
Fastest: 0.0002 secs
Average: 0.0033 secs
Requests/sec: 28923.6075
Status code distribution:

### CBV Chat Completions (stream) (/cbv-chat-completions)

Total: 0.8342 secs
Slowest: 0.0311 secs
Fastest: 0.0005 secs
Average: 0.0080 secs
Requests/sec: 11986.9841
Status code distribution:

## ORM Performance with CBV

### Users CBV Mini10 (List) (/users/cbv-mini10)

Failed requests: 0
Requests per second: 17052.36 [#/sec] (mean)
Time per request: 5.864 [ms] (mean)
Time per request: 0.059 [ms] (mean, across all concurrent requests)

## Form and File Upload Performance

### Form Data (POST /form)

Failed requests: 0
Requests per second: 62487.89 [#/sec] (mean)
Time per request: 1.600 [ms] (mean)
Time per request: 0.016 [ms] (mean, across all concurrent requests)

### File Upload (POST /upload)

Failed requests: 0
Requests per second: 50396.62 [#/sec] (mean)
Time per request: 1.984 [ms] (mean)
Time per request: 0.020 [ms] (mean, across all concurrent requests)

### Mixed Form with Files (POST /mixed-form)

Failed requests: 0
Requests per second: 40088.19 [#/sec] (mean)
Time per request: 2.494 [ms] (mean)
Time per request: 0.025 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks

### JSON Parse/Validate (POST /bench/parse)

Failed requests: 0
Requests per second: 80339.35 [#/sec] (mean)
Time per request: 1.245 [ms] (mean)
Time per request: 0.012 [ms] (mean, across all concurrent requests)
