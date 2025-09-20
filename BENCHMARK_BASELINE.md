# Django-Bolt Benchmark
Generated: Sat Sep 20 11:38:25 PM PKT 2025
Config: 2 processes × 2 workers | C=50 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    44813.91 [#/sec] (mean)
Time per request:       1.116 [ms] (mean)
Time per request:       0.022 [ms] (mean, across all concurrent requests)

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    40030.10 [#/sec] (mean)
Time per request:       1.249 [ms] (mean)
Time per request:       0.025 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    41151.76 [#/sec] (mean)
Time per request:       1.215 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)

## ORM Performance
\n### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    4037.96 [#/sec] (mean)
Time per request:       12.383 [ms] (mean)
Time per request:       0.248 [ms] (mean, across all concurrent requests)
\n### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    4831.09 [#/sec] (mean)
Time per request:       10.350 [ms] (mean)
Time per request:       0.207 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
\n### JSON Parse/Validate (c=1, POST /bench/parse)
Failed requests:        0
Requests per second:    10190.81 [#/sec] (mean)
Time per request:       0.098 [ms] (mean)
Time per request:       0.098 [ms] (mean, across all concurrent requests)
