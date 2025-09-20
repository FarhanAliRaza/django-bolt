# Django-Bolt Benchmark
Generated: Sun Sep 21 12:05:42 AM PKT 2025
Config: 2 processes × 1 workers | C=50 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    44435.36 [#/sec] (mean)
Time per request:       1.125 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    42337.18 [#/sec] (mean)
Time per request:       1.181 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    37809.61 [#/sec] (mean)
Time per request:       1.322 [ms] (mean)
Time per request:       0.026 [ms] (mean, across all concurrent requests)

## ORM Performance
\n### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    3961.56 [#/sec] (mean)
Time per request:       12.621 [ms] (mean)
Time per request:       0.252 [ms] (mean, across all concurrent requests)
\n### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    4673.64 [#/sec] (mean)
Time per request:       10.698 [ms] (mean)
Time per request:       0.214 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
\n### JSON Parse/Validate (c=1, POST /bench/parse)
Failed requests:        0
Requests per second:    9114.21 [#/sec] (mean)
Time per request:       0.110 [ms] (mean)
Time per request:       0.110 [ms] (mean, across all concurrent requests)
