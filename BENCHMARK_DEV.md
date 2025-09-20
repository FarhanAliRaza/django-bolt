# Django-Bolt Benchmark
Generated: Sat Sep 20 11:47:35 PM PKT 2025
Config: 2 processes × 2 workers | C=50 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    43754.29 [#/sec] (mean)
Time per request:       1.143 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    39839.53 [#/sec] (mean)
Time per request:       1.255 [ms] (mean)
Time per request:       0.025 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    38000.71 [#/sec] (mean)
Time per request:       1.316 [ms] (mean)
Time per request:       0.026 [ms] (mean, across all concurrent requests)

## ORM Performance
\n### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    3818.72 [#/sec] (mean)
Time per request:       13.093 [ms] (mean)
Time per request:       0.262 [ms] (mean, across all concurrent requests)
\n### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    4632.26 [#/sec] (mean)
Time per request:       10.794 [ms] (mean)
Time per request:       0.216 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
\n### JSON Parse/Validate (c=1, POST /bench/parse)
Failed requests:        0
Requests per second:    9784.33 [#/sec] (mean)
Time per request:       0.102 [ms] (mean)
Time per request:       0.102 [ms] (mean, across all concurrent requests)
