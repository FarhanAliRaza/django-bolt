# Django-Bolt Benchmark
Generated: Sun Sep 21 12:01:15 AM PKT 2025
Config: 2 processes × 2 workers | C=50 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    44403.40 [#/sec] (mean)
Time per request:       1.126 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    41154.30 [#/sec] (mean)
Time per request:       1.215 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    38980.58 [#/sec] (mean)
Time per request:       1.283 [ms] (mean)
Time per request:       0.026 [ms] (mean, across all concurrent requests)

## ORM Performance
\n### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    3869.67 [#/sec] (mean)
Time per request:       12.921 [ms] (mean)
Time per request:       0.258 [ms] (mean, across all concurrent requests)
\n### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    4628.99 [#/sec] (mean)
Time per request:       10.801 [ms] (mean)
Time per request:       0.216 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
\n### JSON Parse/Validate (c=1, POST /bench/parse)
Failed requests:        0
Requests per second:    9970.26 [#/sec] (mean)
Time per request:       0.100 [ms] (mean)
Time per request:       0.100 [ms] (mean, across all concurrent requests)
