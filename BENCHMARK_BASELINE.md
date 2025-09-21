# Django-Bolt Benchmark
Generated: Sun Sep 21 07:28:24 PM PKT 2025
Config: 4 processes × 1 workers | C=50 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    58054.48 [#/sec] (mean)
Time per request:       0.861 [ms] (mean)
Time per request:       0.017 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
\n### Header Endpoint (/header)
Failed requests:        0
Requests per second:    57789.77 [#/sec] (mean)
Time per request:       0.865 [ms] (mean)
Time per request:       0.017 [ms] (mean, across all concurrent requests)
\n### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    58159.15 [#/sec] (mean)
Time per request:       0.860 [ms] (mean)
Time per request:       0.017 [ms] (mean, across all concurrent requests)
\n### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    57536.41 [#/sec] (mean)
Time per request:       0.869 [ms] (mean)
Time per request:       0.017 [ms] (mean, across all concurrent requests)
\n### HTML Response (/html)
Failed requests:        0
Requests per second:    59582.33 [#/sec] (mean)
Time per request:       0.839 [ms] (mean)
Time per request:       0.017 [ms] (mean, across all concurrent requests)
\n### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    59585.17 [#/sec] (mean)
Time per request:       0.839 [ms] (mean)
Time per request:       0.017 [ms] (mean, across all concurrent requests)

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    53631.67 [#/sec] (mean)
Time per request:       0.932 [ms] (mean)
Time per request:       0.019 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    134226.39 [#/sec] (mean)
Time per request:       0.373 [ms] (mean)
Time per request:       0.007 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    7148.71 [#/sec] (mean)
Time per request:       6.994 [ms] (mean)
Time per request:       0.140 [ms] (mean, across all concurrent requests)
\n### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    8443.02 [#/sec] (mean)
Time per request:       5.922 [ms] (mean)
Time per request:       0.118 [ms] (mean, across all concurrent requests)

## Form and File Upload Performance
\n### Form Data (POST /form)
Failed requests:        0
Requests per second:    44587.92 [#/sec] (mean)
Time per request:       1.121 [ms] (mean)
Time per request:       0.022 [ms] (mean, across all concurrent requests)
\n### File Upload (POST /upload)
Failed requests:        0
Requests per second:    54609.00 [#/sec] (mean)
Time per request:       0.916 [ms] (mean)
Time per request:       0.018 [ms] (mean, across all concurrent requests)
\n### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    54412.00 [#/sec] (mean)
Time per request:       0.919 [ms] (mean)
Time per request:       0.018 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    8976.23 [#/sec] (mean)
Time per request:       0.111 [ms] (mean)
Time per request:       0.111 [ms] (mean, across all concurrent requests)
