# Django-Bolt Benchmark

Generated: Sun Sep 21 12:22:55 AM PKT 2025
Config: 4 processes × 1 workers | C=50 N=10000

## Root Endpoint Performance

Failed requests: 0
Requests per second: 68309.74 [#/sec] (mean)
Time per request: 0.732 [ms] (mean)
Time per request: 0.015 [ms] (mean, across all concurrent requests)

## Items GET Performance (/items/1?q=hello)

Failed requests: 0
Requests per second: 64183.20 [#/sec] (mean)
Time per request: 0.779 [ms] (mean)
Time per request: 0.016 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)

Failed requests: 0
Requests per second: 60909.50 [#/sec] (mean)
Time per request: 0.821 [ms] (mean)
Time per request: 0.016 [ms] (mean, across all concurrent requests)

## ORM Performance

\n### Users Full10 (/users/full10)
Failed requests: 0
Requests per second: 7825.71 [#/sec] (mean)
Time per request: 6.389 [ms] (mean)
Time per request: 0.128 [ms] (mean, across all concurrent requests)
\n### Users Mini10 (/users/mini10)
Failed requests: 0
Requests per second: 9044.03 [#/sec] (mean)
Time per request: 5.529 [ms] (mean)
Time per request: 0.111 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks

\n### JSON Parse/Validate (POST /bench/parse)
Failed requests: 0
Requests per second: 37599.07 [#/sec] (mean)
Time per request: 0.027 [ms] (mean)
Time per request: 0.027 [ms] (mean, across all concurrent requests)
