# Django-Bolt Benchmark
Generated: Sat Sep 20 11:59:12 PM PKT 2025
Config: 2 processes × 2 workers | C=50 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    42766.11 [#/sec] (mean)
Time per request:       1.169 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    40672.73 [#/sec] (mean)
Time per request:       1.229 [ms] (mean)
Time per request:       0.025 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    38428.28 [#/sec] (mean)
Time per request:       1.301 [ms] (mean)
Time per request:       0.026 [ms] (mean, across all concurrent requests)

## ORM Performance
\n### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    3880.03 [#/sec] (mean)
Time per request:       12.887 [ms] (mean)
Time per request:       0.258 [ms] (mean, across all concurrent requests)
\n### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    4691.38 [#/sec] (mean)
Time per request:       10.658 [ms] (mean)
Time per request:       0.213 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
\n### JSON Parse/Validate (c=1, POST /bench/parse)
Failed requests:        0
Requests per second:    10009.21 [#/sec] (mean)
Time per request:       0.100 [ms] (mean)
Time per request:       0.100 [ms] (mean, across all concurrent requests)
