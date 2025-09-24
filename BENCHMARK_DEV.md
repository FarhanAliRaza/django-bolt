# Django-Bolt  Benchmark
Generated: Thu Sep 25 12:18:30 AM PKT 2025
Config: 4 processes × 1 workers | C=100 N=10000 | Mode=bolt

## Root Endpoint Performance
Starting Django-Bolt server...
Failed requests:        0
Requests per second:    48574.58 [#/sec] (mean)
Time per request:       2.059 [ms] (mean)
Time per request:       0.021 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    48711.58 [#/sec] (mean)
Time per request:       2.053 [ms] (mean)
Time per request:       0.021 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    49070.60 [#/sec] (mean)
Time per request:       2.038 [ms] (mean)
Time per request:       0.020 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    47767.13 [#/sec] (mean)
Time per request:       2.093 [ms] (mean)
Time per request:       0.021 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    51158.75 [#/sec] (mean)
Time per request:       1.955 [ms] (mean)
Time per request:       0.020 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    51368.46 [#/sec] (mean)
Time per request:       1.947 [ms] (mean)
Time per request:       0.019 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    2428.73 [#/sec] (mean)
Time per request:       41.174 [ms] (mean)
Time per request:       0.412 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
### Streaming Plain Text (/stream)
  Total:	0.3852 secs
  Slowest:	0.0104 secs
  Fastest:	0.0003 secs
  Average:	0.0038 secs
  Requests/sec:	25957.6603
Status code distribution:
### Server-Sent Events (/sse)
  Total:	0.3492 secs
  Slowest:	0.0213 secs
  Fastest:	0.0002 secs
  Average:	0.0033 secs
  Requests/sec:	28636.5072
Status code distribution:
### Server-Sent Events (async) (/sse-async)
  Total:	0.3125 secs
  Slowest:	0.0115 secs
  Fastest:	0.0002 secs
  Average:	0.0030 secs
  Requests/sec:	31997.3551
Status code distribution:
### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	1.1908 secs
  Slowest:	0.0253 secs
  Fastest:	0.0005 secs
  Average:	0.0114 secs
  Requests/sec:	8398.0074
Status code distribution:
### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	0.3237 secs
  Slowest:	0.0121 secs
  Fastest:	0.0002 secs
  Average:	0.0031 secs
  Requests/sec:	30892.2567
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    41457.48 [#/sec] (mean)
Time per request:       2.412 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    40366.37 [#/sec] (mean)
Time per request:       2.477 [ms] (mean)
Time per request:       0.025 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    7104.46 [#/sec] (mean)
Time per request:       14.076 [ms] (mean)
Time per request:       0.141 [ms] (mean, across all concurrent requests)
### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    8355.35 [#/sec] (mean)
Time per request:       11.968 [ms] (mean)
Time per request:       0.120 [ms] (mean, across all concurrent requests)

## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    37775.05 [#/sec] (mean)
Time per request:       2.647 [ms] (mean)
Time per request:       0.026 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    40955.24 [#/sec] (mean)
Time per request:       2.442 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    39528.19 [#/sec] (mean)
Time per request:       2.530 [ms] (mean)
Time per request:       0.025 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    46769.18 [#/sec] (mean)
Time per request:       2.138 [ms] (mean)
Time per request:       0.021 [ms] (mean, across all concurrent requests)
