# Django-Bolt Benchmark
Generated: Sun Sep 28 06:38:25 PM PKT 2025
Config: 4 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    52905.01 [#/sec] (mean)
Time per request:       1.890 [ms] (mean)
Time per request:       0.019 [ms] (mean, across all concurrent requests)

## Response Type Endpoints

### Header Endpoint (/header)
Failed requests:        0
Requests per second:    50877.90 [#/sec] (mean)
Time per request:       1.965 [ms] (mean)
Time per request:       0.020 [ms] (mean, across all concurrent requests)

### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    49605.39 [#/sec] (mean)
Time per request:       2.016 [ms] (mean)
Time per request:       0.020 [ms] (mean, across all concurrent requests)

### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    50505.56 [#/sec] (mean)
Time per request:       1.980 [ms] (mean)
Time per request:       0.020 [ms] (mean, across all concurrent requests)

### HTML Response (/html)
Failed requests:        0
Requests per second:    52362.05 [#/sec] (mean)
Time per request:       1.910 [ms] (mean)
Time per request:       0.019 [ms] (mean, across all concurrent requests)

### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    53698.77 [#/sec] (mean)
Time per request:       1.862 [ms] (mean)
Time per request:       0.019 [ms] (mean, across all concurrent requests)

### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    2433.21 [#/sec] (mean)
Time per request:       41.098 [ms] (mean)
Time per request:       0.411 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance

### Streaming Plain Text (/stream)
  Total:	0.3479 secs
  Slowest:	0.0093 secs
  Fastest:	0.0002 secs
  Average:	0.0034 secs
  Requests/sec:	28747.2600
Status code distribution:

### Server-Sent Events (/sse)
  Total:	0.3067 secs
  Slowest:	0.0092 secs
  Fastest:	0.0002 secs
  Average:	0.0030 secs
  Requests/sec:	32600.0133
Status code distribution:

### Server-Sent Events (async) (/sse-async)
  Total:	4.1647 secs
  Slowest:	0.0555 secs
  Fastest:	0.0024 secs
  Average:	0.0412 secs
  Requests/sec:	2401.1239
Status code distribution:

### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	1.0564 secs
  Slowest:	0.0211 secs
  Fastest:	0.0004 secs
  Average:	0.0099 secs
  Requests/sec:	9465.7797
Status code distribution:

### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	4.1616 secs
  Slowest:	0.0584 secs
  Fastest:	0.0034 secs
  Average:	0.0412 secs
  Requests/sec:	2402.9428
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    48549.35 [#/sec] (mean)
Time per request:       2.060 [ms] (mean)
Time per request:       0.021 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    47735.66 [#/sec] (mean)
Time per request:       2.095 [ms] (mean)
Time per request:       0.021 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    7358.63 [#/sec] (mean)
Time per request:       13.589 [ms] (mean)
Time per request:       0.136 [ms] (mean, across all concurrent requests)
\n### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    8698.30 [#/sec] (mean)
Time per request:       11.496 [ms] (mean)
Time per request:       0.115 [ms] (mean, across all concurrent requests)

## Form and File Upload Performance
\n### Form Data (POST /form)
Failed requests:        0
Requests per second:    42371.62 [#/sec] (mean)
Time per request:       2.360 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)
\n### File Upload (POST /upload)
Failed requests:        0
Requests per second:    51159.53 [#/sec] (mean)
Time per request:       1.955 [ms] (mean)
Time per request:       0.020 [ms] (mean, across all concurrent requests)
\n### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    51181.00 [#/sec] (mean)
Time per request:       1.954 [ms] (mean)
Time per request:       0.020 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    51763.05 [#/sec] (mean)
Time per request:       1.932 [ms] (mean)
Time per request:       0.019 [ms] (mean, across all concurrent requests)
