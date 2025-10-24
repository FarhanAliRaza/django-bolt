# Django-Bolt Benchmark

Generated: Fri Oct 24 05:46:19 PM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance

Failed requests: 0
Requests per second: 87183.20 [#/sec] (mean)
Time per request: 1.147 [ms] (mean)
Time per request: 0.011 [ms] (mean, across all concurrent requests)

## 10kb JSON Response Performance

### 10kb JSON (/10k-json)

Failed requests: 0
Requests per second: 70692.86 [#/sec] (mean)
Time per request: 1.415 [ms] (mean)
Time per request: 0.014 [ms] (mean, across all concurrent requests)

## Response Type Endpoints

### Header Endpoint (/header)

Failed requests: 0
Requests per second: 84417.39 [#/sec] (mean)
Time per request: 1.185 [ms] (mean)
Time per request: 0.012 [ms] (mean, across all concurrent requests)

### Cookie Endpoint (/cookie)

Failed requests: 0
Requests per second: 84801.82 [#/sec] (mean)
Time per request: 1.179 [ms] (mean)
Time per request: 0.012 [ms] (mean, across all concurrent requests)

### Exception Endpoint (/exc)

Failed requests: 0
Requests per second: 80854.47 [#/sec] (mean)
Time per request: 1.237 [ms] (mean)
Time per request: 0.012 [ms] (mean, across all concurrent requests)

### HTML Response (/html)

Failed requests: 0
Requests per second: 83965.17 [#/sec] (mean)
Time per request: 1.191 [ms] (mean)
Time per request: 0.012 [ms] (mean, across all concurrent requests)

### Redirect Response (/redirect)

Failed requests: 0
Requests per second: 86233.66 [#/sec] (mean)
Time per request: 1.160 [ms] (mean)
Time per request: 0.012 [ms] (mean, across all concurrent requests)

### File Static via FileResponse (/file-static)

Failed requests: 0
Requests per second: 29754.91 [#/sec] (mean)
Time per request: 3.361 [ms] (mean)
Time per request: 0.034 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance

### Streaming Plain Text (/stream)

Total: 0.2257 secs
Slowest: 0.0204 secs
Fastest: 0.0002 secs
Average: 0.0022 secs
Requests/sec: 44304.1808
Status code distribution:

### Server-Sent Events (/sse)

Total: 0.1886 secs
Slowest: 0.0086 secs
Fastest: 0.0001 secs
Average: 0.0018 secs
Requests/sec: 53013.3799
Status code distribution:

### Server-Sent Events (async) (/sse-async)

Total: 0.3740 secs
Slowest: 0.0127 secs
Fastest: 0.0002 secs
Average: 0.0035 secs
Requests/sec: 26737.0049
Status code distribution:

### OpenAI Chat Completions (stream) (/v1/chat/completions)

Total: 0.6987 secs
Slowest: 0.0294 secs
Fastest: 0.0004 secs
Average: 0.0065 secs
Requests/sec: 14311.5372
Status code distribution:

### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)

Total: 0.8044 secs
Slowest: 0.0264 secs
Fastest: 0.0004 secs
Average: 0.0076 secs
Requests/sec: 12431.5822
Status code distribution:

## Items GET Performance (/items/1?q=hello)

Failed requests: 0
Requests per second: 80854.47 [#/sec] (mean)
Time per request: 1.237 [ms] (mean)
Time per request: 0.012 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)

Failed requests: 0
Requests per second: 72544.20 [#/sec] (mean)
Time per request: 1.378 [ms] (mean)
Time per request: 0.014 [ms] (mean, across all concurrent requests)

## ORM Performance

### Users Full10 (/users/full10)

Failed requests: 0
Requests per second: 13839.93 [#/sec] (mean)
Time per request: 7.225 [ms] (mean)
Time per request: 0.072 [ms] (mean, across all concurrent requests)

### Users Mini10 (/users/mini10)

Failed requests: 0
Requests per second: 13976.96 [#/sec] (mean)
Time per request: 7.155 [ms] (mean)
Time per request: 0.072 [ms] (mean, across all concurrent requests)

## Class-Based Views (CBV) Performance

### Simple APIView GET (/cbv-simple)

Failed requests: 0
Requests per second: 80564.60 [#/sec] (mean)
Time per request: 1.241 [ms] (mean)
Time per request: 0.012 [ms] (mean, across all concurrent requests)

### Simple APIView POST (/cbv-simple)

Failed requests: 0
Requests per second: 75386.36 [#/sec] (mean)
Time per request: 1.326 [ms] (mean)
Time per request: 0.013 [ms] (mean, across all concurrent requests)

### Items100 ViewSet GET (/cbv-items100)

Failed requests: 0
Requests per second: 58646.21 [#/sec] (mean)
Time per request: 1.705 [ms] (mean)
Time per request: 0.017 [ms] (mean, across all concurrent requests)

## CBV Items - Basic Operations

### CBV Items GET (Retrieve) (/cbv-items/1)

Failed requests: 0
Requests per second: 78213.60 [#/sec] (mean)
Time per request: 1.279 [ms] (mean)
Time per request: 0.013 [ms] (mean, across all concurrent requests)

### CBV Items PUT (Update) (/cbv-items/1)

Failed requests: 0
Requests per second: 76398.28 [#/sec] (mean)
Time per request: 1.309 [ms] (mean)
Time per request: 0.013 [ms] (mean, across all concurrent requests)

## CBV Additional Benchmarks

### CBV Bench Parse (POST /cbv-bench-parse)

Failed requests: 0
Requests per second: 76617.20 [#/sec] (mean)
Time per request: 1.305 [ms] (mean)
Time per request: 0.013 [ms] (mean, across all concurrent requests)

### CBV Response Types (/cbv-response)

Failed requests: 0
Requests per second: 86009.67 [#/sec] (mean)
Time per request: 1.163 [ms] (mean)
Time per request: 0.012 [ms] (mean, across all concurrent requests)

### CBV Streaming Plain Text (/cbv-stream)

Total: 0.3938 secs
Slowest: 0.0206 secs
Fastest: 0.0002 secs
Average: 0.0038 secs
Requests/sec: 25393.5052
Status code distribution:

### CBV Server-Sent Events (/cbv-sse)

Total: 0.3647 secs
Slowest: 0.0180 secs
Fastest: 0.0002 secs
Average: 0.0034 secs
Requests/sec: 27418.8288
Status code distribution:

### CBV Chat Completions (stream) (/cbv-chat-completions)

Total: 0.8309 secs
Slowest: 0.0292 secs
Fastest: 0.0005 secs
Average: 0.0080 secs
Requests/sec: 12034.7346
Status code distribution:

## ORM Performance with CBV

### Users CBV Mini10 (List) (/users/cbv-mini10)

Failed requests: 0
Requests per second: 17062.11 [#/sec] (mean)
Time per request: 5.861 [ms] (mean)
Time per request: 0.059 [ms] (mean, across all concurrent requests)

## Form and File Upload Performance

### Form Data (POST /form)

Failed requests: 0
Requests per second: 63357.70 [#/sec] (mean)
Time per request: 1.578 [ms] (mean)
Time per request: 0.016 [ms] (mean, across all concurrent requests)

### File Upload (POST /upload)

Failed requests: 0
Requests per second: 50881.78 [#/sec] (mean)
Time per request: 1.965 [ms] (mean)
Time per request: 0.020 [ms] (mean, across all concurrent requests)

### Mixed Form with Files (POST /mixed-form)

Failed requests: 0
Requests per second: 48102.36 [#/sec] (mean)
Time per request: 2.079 [ms] (mean)
Time per request: 0.021 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks

### JSON Parse/Validate (POST /bench/parse)

Failed requests: 0
Requests per second: 76979.33 [#/sec] (mean)
Time per request: 1.299 [ms] (mean)
Time per request: 0.013 [ms] (mean, across all concurrent requests)
