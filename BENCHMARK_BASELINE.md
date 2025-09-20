# Django-Bolt Benchmark
Generated: Sun Sep 21 12:22:31 AM PKT 2025
Config: 4 processes × 1 workers | C=50 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    66699.13 [#/sec] (mean)
Time per request:       0.750 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    66060.67 [#/sec] (mean)
Time per request:       0.757 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    59092.23 [#/sec] (mean)
Time per request:       0.846 [ms] (mean)
Time per request:       0.017 [ms] (mean, across all concurrent requests)

## ORM Performance
\n### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    7932.03 [#/sec] (mean)
Time per request:       6.304 [ms] (mean)
Time per request:       0.126 [ms] (mean, across all concurrent requests)
\n### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    9125.06 [#/sec] (mean)
Time per request:       5.479 [ms] (mean)
Time per request:       0.110 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
\n### JSON Parse/Validate (c=1, POST /bench/parse)
Failed requests:        0
Requests per second:    37689.48 [#/sec] (mean)
Time per request:       0.027 [ms] (mean)
Time per request:       0.027 [ms] (mean, across all concurrent requests)
