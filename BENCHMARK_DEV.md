# Django-Bolt Benchmark
Generated: Sat Oct 11 07:17:48 PM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    82029.74 [#/sec] (mean)
Time per request:       1.219 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    78658.40 [#/sec] (mean)
Time per request:       1.271 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    76478.91 [#/sec] (mean)
Time per request:       1.308 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    78104.25 [#/sec] (mean)
Time per request:       1.280 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    74611.28 [#/sec] (mean)
Time per request:       1.340 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    76900.60 [#/sec] (mean)
Time per request:       1.300 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    2429.98 [#/sec] (mean)
Time per request:       41.153 [ms] (mean)
Time per request:       0.412 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
### Streaming Plain Text (/stream)
  Total:	0.2075 secs
  Slowest:	0.0114 secs
  Fastest:	0.0002 secs
  Average:	0.0020 secs
  Requests/sec:	48200.0859
Status code distribution:
### Server-Sent Events (/sse)
  Total:	0.1944 secs
  Slowest:	0.0090 secs
  Fastest:	0.0002 secs
  Average:	0.0019 secs
  Requests/sec:	51445.1652
Status code distribution:
### Server-Sent Events (async) (/sse-async)
  Total:	0.4087 secs
  Slowest:	0.0948 secs
  Fastest:	0.0003 secs
  Average:	0.0039 secs
  Requests/sec:	24468.4568
Status code distribution:
### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	0.5425 secs
  Slowest:	0.0226 secs
  Fastest:	0.0004 secs
  Average:	0.0052 secs
  Requests/sec:	18434.2734
Status code distribution:
### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	0.6500 secs
  Slowest:	0.0303 secs
  Fastest:	0.0005 secs
  Average:	0.0062 secs
  Requests/sec:	15384.3426
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    73479.16 [#/sec] (mean)
Time per request:       1.361 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    70189.72 [#/sec] (mean)
Time per request:       1.425 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    12062.62 [#/sec] (mean)
Time per request:       8.290 [ms] (mean)
Time per request:       0.083 [ms] (mean, across all concurrent requests)
### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    14934.20 [#/sec] (mean)
Time per request:       6.696 [ms] (mean)
Time per request:       0.067 [ms] (mean, across all concurrent requests)

## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    64341.37 [#/sec] (mean)
Time per request:       1.554 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    21537.29 [#/sec] (mean)
Time per request:       4.643 [ms] (mean)
Time per request:       0.046 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    22014.21 [#/sec] (mean)
Time per request:       4.543 [ms] (mean)
Time per request:       0.045 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    75563.51 [#/sec] (mean)
Time per request:       1.323 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
