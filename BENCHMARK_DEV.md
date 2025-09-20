# Django-Bolt Benchmark
Generated: Sun Sep 21 12:06:57 AM PKT 2025
Config: 4 processes × 1 workers | C=50 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    64527.79 [#/sec] (mean)
Time per request:       0.775 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    67866.55 [#/sec] (mean)
Time per request:       0.737 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    61265.50 [#/sec] (mean)
Time per request:       0.816 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)

## ORM Performance
\n### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    7507.36 [#/sec] (mean)
Time per request:       6.660 [ms] (mean)
Time per request:       0.133 [ms] (mean, across all concurrent requests)
\n### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    8944.02 [#/sec] (mean)
Time per request:       5.590 [ms] (mean)
Time per request:       0.112 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
\n### JSON Parse/Validate (c=1, POST /bench/parse)
Failed requests:        0
Requests per second:    9023.87 [#/sec] (mean)
Time per request:       0.111 [ms] (mean)
Time per request:       0.111 [ms] (mean, across all concurrent requests)
