# Django-Bolt Benchmark
Generated: Sun Sep 21 07:24:24 PM PKT 2025
Config: 4 processes × 1 workers | C=50 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    58266.57 [#/sec] (mean)
Time per request:       0.858 [ms] (mean)
Time per request:       0.017 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
\n### Header Endpoint (/header)
Failed requests:        0
Requests per second:    56576.77 [#/sec] (mean)
Time per request:       0.884 [ms] (mean)
Time per request:       0.018 [ms] (mean, across all concurrent requests)
\n### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    56403.17 [#/sec] (mean)
Time per request:       0.886 [ms] (mean)
Time per request:       0.018 [ms] (mean, across all concurrent requests)
\n### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    56739.20 [#/sec] (mean)
Time per request:       0.881 [ms] (mean)
Time per request:       0.018 [ms] (mean, across all concurrent requests)
\n### HTML Response (/html)
Failed requests:        0
Requests per second:    59465.05 [#/sec] (mean)
Time per request:       0.841 [ms] (mean)
Time per request:       0.017 [ms] (mean, across all concurrent requests)
\n### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    59556.42 [#/sec] (mean)
Time per request:       0.840 [ms] (mean)
Time per request:       0.017 [ms] (mean, across all concurrent requests)

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    54106.99 [#/sec] (mean)
Time per request:       0.924 [ms] (mean)
Time per request:       0.018 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    48755.52 [#/sec] (mean)
Time per request:       1.026 [ms] (mean)
Time per request:       0.021 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    7111.56 [#/sec] (mean)
Time per request:       7.031 [ms] (mean)
Time per request:       0.141 [ms] (mean, across all concurrent requests)
\n### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    8160.95 [#/sec] (mean)
Time per request:       6.127 [ms] (mean)
Time per request:       0.123 [ms] (mean, across all concurrent requests)

## Form and File Upload Performance
\n### Form Data (POST /form)
Failed requests:        0
Requests per second:    133228.53 [#/sec] (mean)
Time per request:       0.375 [ms] (mean)
Time per request:       0.008 [ms] (mean, across all concurrent requests)
\n### File Upload (POST /upload)
Failed requests:        0
Requests per second:    130802.74 [#/sec] (mean)
Time per request:       0.382 [ms] (mean)
Time per request:       0.008 [ms] (mean, across all concurrent requests)
\n### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    128627.29 [#/sec] (mean)
Time per request:       0.389 [ms] (mean)
Time per request:       0.008 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    33279.75 [#/sec] (mean)
Time per request:       0.030 [ms] (mean)
Time per request:       0.030 [ms] (mean, across all concurrent requests)
