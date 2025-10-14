# Django-Bolt Benchmark
Generated: Wed Oct 15 12:29:36 AM PKT 2025
Config: 4 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    40341.29 [#/sec] (mean)
Time per request:       2.479 [ms] (mean)
Time per request:       0.025 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    41680.39 [#/sec] (mean)
Time per request:       2.399 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    42698.18 [#/sec] (mean)
Time per request:       2.342 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    39605.37 [#/sec] (mean)
Time per request:       2.525 [ms] (mean)
Time per request:       0.025 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    42665.21 [#/sec] (mean)
Time per request:       2.344 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    43725.21 [#/sec] (mean)
Time per request:       2.287 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    23979.09 [#/sec] (mean)
Time per request:       4.170 [ms] (mean)
Time per request:       0.042 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
### Streaming Plain Text (/stream)
  Total:	0.3916 secs
  Slowest:	0.0104 secs
  Fastest:	0.0001 secs
  Average:	0.0038 secs
  Requests/sec:	25536.2025
Status code distribution:
### Server-Sent Events (/sse)
  Total:	0.3521 secs
  Slowest:	0.0084 secs
  Fastest:	0.0002 secs
  Average:	0.0034 secs
  Requests/sec:	28398.7825
Status code distribution:
### Server-Sent Events (async) (/sse-async)
  Total:	0.7331 secs
  Slowest:	0.0162 secs
  Fastest:	0.0003 secs
  Average:	0.0071 secs
  Requests/sec:	13640.5061
Status code distribution:
### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	1.1083 secs
  Slowest:	0.0215 secs
  Fastest:	0.0004 secs
  Average:	0.0105 secs
  Requests/sec:	9022.9013
Status code distribution:
### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	1.5949 secs
  Slowest:	0.0301 secs
  Fastest:	0.0005 secs
  Average:	0.0144 secs
  Requests/sec:	6269.9100
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    39832.07 [#/sec] (mean)
Time per request:       2.511 [ms] (mean)
Time per request:       0.025 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    35618.37 [#/sec] (mean)
Time per request:       2.808 [ms] (mean)
Time per request:       0.028 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    7079.50 [#/sec] (mean)
Time per request:       14.125 [ms] (mean)
Time per request:       0.141 [ms] (mean, across all concurrent requests)
### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    8323.91 [#/sec] (mean)
Time per request:       12.014 [ms] (mean)
Time per request:       0.120 [ms] (mean, across all concurrent requests)

## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    35063.36 [#/sec] (mean)
Time per request:       2.852 [ms] (mean)
Time per request:       0.029 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    7416.04 [#/sec] (mean)
Time per request:       13.484 [ms] (mean)
Time per request:       0.135 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    7459.21 [#/sec] (mean)
Time per request:       13.406 [ms] (mean)
Time per request:       0.134 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    40318.03 [#/sec] (mean)
Time per request:       2.480 [ms] (mean)
Time per request:       0.025 [ms] (mean, across all concurrent requests)
