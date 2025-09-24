# Django-Bolt  Benchmark
Generated: Thu Sep 25 12:17:18 AM PKT 2025
Config: 4 processes × 1 workers | C=100 N=10000 | Mode=bolt

## Root Endpoint Performance
Starting Django-Bolt server...
Failed requests:        0
Requests per second:    46613.96 [#/sec] (mean)
Time per request:       2.145 [ms] (mean)
Time per request:       0.021 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    46907.40 [#/sec] (mean)
Time per request:       2.132 [ms] (mean)
Time per request:       0.021 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    46453.94 [#/sec] (mean)
Time per request:       2.153 [ms] (mean)
Time per request:       0.022 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    46072.97 [#/sec] (mean)
Time per request:       2.170 [ms] (mean)
Time per request:       0.022 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    48411.38 [#/sec] (mean)
Time per request:       2.066 [ms] (mean)
Time per request:       0.021 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    51116.64 [#/sec] (mean)
Time per request:       1.956 [ms] (mean)
Time per request:       0.020 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    2438.70 [#/sec] (mean)
Time per request:       41.005 [ms] (mean)
Time per request:       0.410 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
### Streaming Plain Text (/stream)
  Total:	0.3584 secs
  Slowest:	0.0098 secs
  Fastest:	0.0002 secs
  Average:	0.0034 secs
  Requests/sec:	27900.0581
Status code distribution:
### Server-Sent Events (/sse)
  Total:	0.3016 secs
  Slowest:	0.0101 secs
  Fastest:	0.0001 secs
  Average:	0.0029 secs
  Requests/sec:	33161.9032
Status code distribution:
### Server-Sent Events (async) (/sse-async)
  Total:	0.2844 secs
  Slowest:	0.0098 secs
  Fastest:	0.0001 secs
  Average:	0.0028 secs
  Requests/sec:	35163.6167
Status code distribution:
### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	1.1272 secs
  Slowest:	0.0235 secs
  Fastest:	0.0004 secs
  Average:	0.0107 secs
  Requests/sec:	8871.9084
Status code distribution:
### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	0.2977 secs
  Slowest:	0.0114 secs
  Fastest:	0.0002 secs
  Average:	0.0029 secs
  Requests/sec:	33594.9530
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    47072.56 [#/sec] (mean)
Time per request:       2.124 [ms] (mean)
Time per request:       0.021 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    44257.77 [#/sec] (mean)
Time per request:       2.259 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    7010.39 [#/sec] (mean)
Time per request:       14.265 [ms] (mean)
Time per request:       0.143 [ms] (mean, across all concurrent requests)
### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    8406.17 [#/sec] (mean)
Time per request:       11.896 [ms] (mean)
Time per request:       0.119 [ms] (mean, across all concurrent requests)

## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    41704.90 [#/sec] (mean)
Time per request:       2.398 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    43354.61 [#/sec] (mean)
Time per request:       2.307 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    41294.33 [#/sec] (mean)
Time per request:       2.422 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    51310.47 [#/sec] (mean)
Time per request:       1.949 [ms] (mean)
Time per request:       0.019 [ms] (mean, across all concurrent requests)
