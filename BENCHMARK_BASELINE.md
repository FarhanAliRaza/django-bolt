# Django-Bolt Benchmark
Generated: Sun Sep 21 10:36:28 AM PKT 2025
Config: 4 processes × 1 workers | C=50 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    66860.56 [#/sec] (mean)
Time per request:       0.748 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)

## Header/Cookie/Exception/HTML/Redirect/File Endpoints
Failed requests:        0
Requests per second:    64221.54 [#/sec] (mean)
Time per request:       0.779 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)
Failed requests:        0
Requests per second:    61784.46 [#/sec] (mean)
Time per request:       0.809 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)
Failed requests:        0
Requests per second:    66294.53 [#/sec] (mean)
Time per request:       0.754 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)
Failed requests:        0
Requests per second:    63910.83 [#/sec] (mean)
Time per request:       0.782 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)
Failed requests:        0
Requests per second:    60556.88 [#/sec] (mean)
Time per request:       0.826 [ms] (mean)
Time per request:       0.017 [ms] (mean, across all concurrent requests)

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    59549.33 [#/sec] (mean)
Time per request:       0.840 [ms] (mean)
Time per request:       0.017 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    52182.26 [#/sec] (mean)
Time per request:       0.958 [ms] (mean)
Time per request:       0.019 [ms] (mean, across all concurrent requests)

## ORM Performance
\n### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    7684.38 [#/sec] (mean)
Time per request:       6.507 [ms] (mean)
Time per request:       0.130 [ms] (mean, across all concurrent requests)
\n### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    8689.00 [#/sec] (mean)
Time per request:       5.754 [ms] (mean)
Time per request:       0.115 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
\n### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    40457.17 [#/sec] (mean)
Time per request:       0.025 [ms] (mean)
Time per request:       0.025 [ms] (mean, across all concurrent requests)
