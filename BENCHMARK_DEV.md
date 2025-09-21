# Django-Bolt Benchmark
Generated: Sun Sep 21 08:49:53 PM PKT 2025
Config: 4 processes × 1 workers | C=50 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    65491.74 [#/sec] (mean)
Time per request:       0.763 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
\n### Header Endpoint (/header)
Failed requests:        0
Requests per second:    65667.64 [#/sec] (mean)
Time per request:       0.761 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)
\n### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    65588.39 [#/sec] (mean)
Time per request:       0.762 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)
\n### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    65104.59 [#/sec] (mean)
Time per request:       0.768 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)
\n### HTML Response (/html)
Failed requests:        0
Requests per second:    65830.62 [#/sec] (mean)
Time per request:       0.760 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)
\n### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    67694.72 [#/sec] (mean)
Time per request:       0.739 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)
\n### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    59548.98 [#/sec] (mean)
Time per request:       0.840 [ms] (mean)
Time per request:       0.017 [ms] (mean, across all concurrent requests)

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    62863.43 [#/sec] (mean)
Time per request:       0.795 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    147383.94 [#/sec] (mean)
Time per request:       0.339 [ms] (mean)
Time per request:       0.007 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    7551.18 [#/sec] (mean)
Time per request:       6.621 [ms] (mean)
Time per request:       0.132 [ms] (mean, across all concurrent requests)
\n### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    8756.01 [#/sec] (mean)
Time per request:       5.710 [ms] (mean)
Time per request:       0.114 [ms] (mean, across all concurrent requests)

## Form and File Upload Performance
\n### Form Data (POST /form)
Failed requests:        0
Requests per second:    48060.29 [#/sec] (mean)
Time per request:       1.040 [ms] (mean)
Time per request:       0.021 [ms] (mean, across all concurrent requests)
\n### File Upload (POST /upload)
Failed requests:        0
Requests per second:    60613.41 [#/sec] (mean)
Time per request:       0.825 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)
\n### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    61536.95 [#/sec] (mean)
Time per request:       0.813 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    9800.04 [#/sec] (mean)
Time per request:       0.102 [ms] (mean)
Time per request:       0.102 [ms] (mean, across all concurrent requests)
