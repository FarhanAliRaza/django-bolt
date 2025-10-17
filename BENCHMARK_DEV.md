# Django-Bolt Benchmark
Generated: Fri Oct 17 08:46:02 PM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    75954.94 [#/sec] (mean)
Time per request:       1.317 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    77158.71 [#/sec] (mean)
Time per request:       1.296 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    74080.66 [#/sec] (mean)
Time per request:       1.350 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    77291.10 [#/sec] (mean)
Time per request:       1.294 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    80437.58 [#/sec] (mean)
Time per request:       1.243 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    78185.47 [#/sec] (mean)
Time per request:       1.279 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    22967.60 [#/sec] (mean)
Time per request:       4.354 [ms] (mean)
Time per request:       0.044 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
### Streaming Plain Text (/stream)
  Total:	0.2401 secs
  Slowest:	0.0113 secs
  Fastest:	0.0002 secs
  Average:	0.0023 secs
  Requests/sec:	41653.5933
Status code distribution:
### Server-Sent Events (/sse)
  Total:	0.2154 secs
  Slowest:	0.0144 secs
  Fastest:	0.0002 secs
  Average:	0.0020 secs
  Requests/sec:	46435.4593
Status code distribution:
### Server-Sent Events (async) (/sse-async)
  Total:	0.3878 secs
  Slowest:	0.0142 secs
  Fastest:	0.0003 secs
  Average:	0.0037 secs
  Requests/sec:	25787.8867
Status code distribution:
### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	0.7071 secs
  Slowest:	0.0320 secs
  Fastest:	0.0004 secs
  Average:	0.0068 secs
  Requests/sec:	14143.0279
Status code distribution:
### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	0.8261 secs
  Slowest:	0.0246 secs
  Fastest:	0.0005 secs
  Average:	0.0077 secs
  Requests/sec:	12105.6532
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    75274.56 [#/sec] (mean)
Time per request:       1.328 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    66394.89 [#/sec] (mean)
Time per request:       1.506 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    10477.74 [#/sec] (mean)
Time per request:       9.544 [ms] (mean)
Time per request:       0.095 [ms] (mean, across all concurrent requests)
### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    12459.48 [#/sec] (mean)
Time per request:       8.026 [ms] (mean)
Time per request:       0.080 [ms] (mean, across all concurrent requests)

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
Failed requests:        0
Requests per second:    83037.86 [#/sec] (mean)
Time per request:       1.204 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### Simple APIView POST (/cbv-simple)
Failed requests:        0
Requests per second:    75299.50 [#/sec] (mean)
Time per request:       1.328 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### Items100 ViewSet GET (/cbv-items100)
Failed requests:        0
Requests per second:    37947.21 [#/sec] (mean)
Time per request:       2.635 [ms] (mean)
Time per request:       0.026 [ms] (mean, across all concurrent requests)

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
Failed requests:        0
Requests per second:    74649.71 [#/sec] (mean)
Time per request:       1.340 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### CBV Items PUT (Update) (/cbv-items/1)
Failed requests:        0
Requests per second:    73702.29 [#/sec] (mean)
Time per request:       1.357 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
Failed requests:        0
Requests per second:    67092.03 [#/sec] (mean)
Time per request:       1.490 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)
### CBV Response Types (/cbv-response)
Failed requests:        0
Requests per second:    69003.59 [#/sec] (mean)
Time per request:       1.449 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)
### CBV Streaming Plain Text (/cbv-stream)
  Total:	0.3981 secs
  Slowest:	0.0212 secs
  Fastest:	0.0002 secs
  Average:	0.0038 secs
  Requests/sec:	25119.7338
Status code distribution:
### CBV Server-Sent Events (/cbv-sse)
  Total:	0.4048 secs
  Slowest:	0.0222 secs
  Fastest:	0.0002 secs
  Average:	0.0039 secs
  Requests/sec:	24700.5643
Status code distribution:
### CBV Chat Completions (stream) (/cbv-chat-completions)
  Total:	0.9479 secs
  Slowest:	0.0401 secs
  Fastest:	0.0005 secs
  Average:	0.0091 secs
  Requests/sec:	10549.3154
Status code distribution:

## ORM Performance with CBV
### Users CBV Mini10 (List) (/users/cbv-mini10)
Failed requests:        0
Requests per second:    15847.86 [#/sec] (mean)
Time per request:       6.310 [ms] (mean)
Time per request:       0.063 [ms] (mean, across all concurrent requests)


## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    64057.40 [#/sec] (mean)
Time per request:       1.561 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    12705.27 [#/sec] (mean)
Time per request:       7.871 [ms] (mean)
Time per request:       0.079 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    12866.37 [#/sec] (mean)
Time per request:       7.772 [ms] (mean)
Time per request:       0.078 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    75504.18 [#/sec] (mean)
Time per request:       1.324 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
