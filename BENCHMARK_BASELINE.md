# Django-Bolt Benchmark
Generated: Mon Oct 13 06:08:58 PM PKT 2025
Config: 4 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    77380.81 [#/sec] (mean)
Time per request:       1.292 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    80723.93 [#/sec] (mean)
Time per request:       1.239 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    79879.22 [#/sec] (mean)
Time per request:       1.252 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    77049.91 [#/sec] (mean)
Time per request:       1.298 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    79824.39 [#/sec] (mean)
Time per request:       1.253 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    83243.85 [#/sec] (mean)
Time per request:       1.201 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    2431.51 [#/sec] (mean)
Time per request:       41.127 [ms] (mean)
Time per request:       0.411 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
### Streaming Plain Text (/stream)
  Total:	0.2212 secs
  Slowest:	0.0096 secs
  Fastest:	0.0002 secs
  Average:	0.0021 secs
  Requests/sec:	45212.2933
Status code distribution:
### Server-Sent Events (/sse)
  Total:	0.2632 secs
  Slowest:	0.0144 secs
  Fastest:	0.0002 secs
  Average:	0.0025 secs
  Requests/sec:	38000.5815
Status code distribution:
### Server-Sent Events (async) (/sse-async)
  Total:	0.3993 secs
  Slowest:	0.0173 secs
  Fastest:	0.0003 secs
  Average:	0.0038 secs
  Requests/sec:	25045.6326
Status code distribution:
### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	0.6858 secs
  Slowest:	0.0260 secs
  Fastest:	0.0004 secs
  Average:	0.0064 secs
  Requests/sec:	14581.4068
Status code distribution:
### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	0.8355 secs
  Slowest:	0.0262 secs
  Fastest:	0.0005 secs
  Average:	0.0079 secs
  Requests/sec:	11969.5524
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    76700.65 [#/sec] (mean)
Time per request:       1.304 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    71167.79 [#/sec] (mean)
Time per request:       1.405 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    7122.54 [#/sec] (mean)
Time per request:       14.040 [ms] (mean)
Time per request:       0.140 [ms] (mean, across all concurrent requests)
### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    7969.42 [#/sec] (mean)
Time per request:       12.548 [ms] (mean)
Time per request:       0.125 [ms] (mean, across all concurrent requests)

## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    34371.35 [#/sec] (mean)
Time per request:       2.909 [ms] (mean)
Time per request:       0.029 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    11934.54 [#/sec] (mean)
Time per request:       8.379 [ms] (mean)
Time per request:       0.084 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    11918.88 [#/sec] (mean)
Time per request:       8.390 [ms] (mean)
Time per request:       0.084 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    41771.79 [#/sec] (mean)
Time per request:       2.394 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)
