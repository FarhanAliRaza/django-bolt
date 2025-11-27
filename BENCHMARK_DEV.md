# Django-Bolt Benchmark
Generated: Thu Nov 27 05:22:28 PM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    103454.34 [#/sec] (mean)
Time per request:       0.967 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## 10kb JSON Response Performance
### 10kb JSON (Async) (/10k-json)
Failed requests:        0
Requests per second:    84185.71 [#/sec] (mean)
Time per request:       1.188 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### 10kb JSON (Sync) (/sync-10k-json)
Failed requests:        0
Requests per second:    63701.57 [#/sec] (mean)
Time per request:       1.570 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    100722.18 [#/sec] (mean)
Time per request:       0.993 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    99791.44 [#/sec] (mean)
Time per request:       1.002 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    99127.68 [#/sec] (mean)
Time per request:       1.009 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    102928.31 [#/sec] (mean)
Time per request:       0.972 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    81019.55 [#/sec] (mean)
Time per request:       1.234 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    26810.08 [#/sec] (mean)
Time per request:       3.730 [ms] (mean)
Time per request:       0.037 [ms] (mean, across all concurrent requests)

## Authentication & Authorization Performance
### Get Authenticated User (/auth/me)
Failed requests:        0
Requests per second:    13917.26 [#/sec] (mean)
Time per request:       7.185 [ms] (mean)
Time per request:       0.072 [ms] (mean, across all concurrent requests)
### Get User via Dependency (/auth/me-dependency)
Failed requests:        0
Requests per second:    7964.05 [#/sec] (mean)
Time per request:       12.556 [ms] (mean)
Time per request:       0.126 [ms] (mean, across all concurrent requests)
### Get Auth Context (/auth/context) validated jwt no db
Failed requests:        0
Requests per second:    88458.78 [#/sec] (mean)
Time per request:       1.130 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
SEE STREAMING_BENCHMARK_DEV.md

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    92253.48 [#/sec] (mean)
Time per request:       1.084 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    92960.13 [#/sec] (mean)
Time per request:       1.076 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

## ORM Performance
Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users Full10 (Async) (/users/full10)
Failed requests:        0
Requests per second:    16019.30 [#/sec] (mean)
Time per request:       6.242 [ms] (mean)
Time per request:       0.062 [ms] (mean, across all concurrent requests)
### Users Full10 (Sync) (/users/sync-full10)
Failed requests:        0
Requests per second:    12626.26 [#/sec] (mean)
Time per request:       7.920 [ms] (mean)
Time per request:       0.079 [ms] (mean, across all concurrent requests)
### Users Mini10 (Async) (/users/mini10)
Failed requests:        0
Requests per second:    17792.61 [#/sec] (mean)
Time per request:       5.620 [ms] (mean)
Time per request:       0.056 [ms] (mean, across all concurrent requests)
### Users Mini10 (Sync) (/users/sync-mini10)
Failed requests:        0
Requests per second:    17218.79 [#/sec] (mean)
Time per request:       5.808 [ms] (mean)
Time per request:       0.058 [ms] (mean, across all concurrent requests)
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
Failed requests:        0
Requests per second:    101290.44 [#/sec] (mean)
Time per request:       0.987 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Simple APIView POST (/cbv-simple)
Failed requests:        0
Requests per second:    97361.50 [#/sec] (mean)
Time per request:       1.027 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Items100 ViewSet GET (/cbv-items100)
Failed requests:        0
Requests per second:    69453.13 [#/sec] (mean)
Time per request:       1.440 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
Failed requests:        0
Requests per second:    95337.06 [#/sec] (mean)
Time per request:       1.049 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### CBV Items PUT (Update) (/cbv-items/1)
Failed requests:        0
Requests per second:    74757.41 [#/sec] (mean)
Time per request:       1.338 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
Failed requests:        0
Requests per second:    101442.51 [#/sec] (mean)
Time per request:       0.986 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### CBV Response Types (/cbv-response)
Failed requests:        0
Requests per second:    96404.13 [#/sec] (mean)
Time per request:       1.037 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users CBV Mini10 (List) (/users/cbv-mini10)
Failed requests:        0
Requests per second:    18015.62 [#/sec] (mean)
Time per request:       5.551 [ms] (mean)
Time per request:       0.056 [ms] (mean, across all concurrent requests)
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    79260.03 [#/sec] (mean)
Time per request:       1.262 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    58022.81 [#/sec] (mean)
Time per request:       1.723 [ms] (mean)
Time per request:       0.017 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    58597.07 [#/sec] (mean)
Time per request:       1.707 [ms] (mean)
Time per request:       0.017 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    99838.26 [#/sec] (mean)
Time per request:       1.002 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## Serializer Performance Benchmarks
### Raw msgspec Serializer (POST /bench/serializer-raw)
Failed requests:        0
Requests per second:    95689.20 [#/sec] (mean)
Time per request:       1.045 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Django-Bolt Serializer with Validators (POST /bench/serializer-validated)
Failed requests:        0
Requests per second:    87443.16 [#/sec] (mean)
Time per request:       1.144 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### Users msgspec Serializer (POST /users/bench/msgspec)
Failed requests:        0
Requests per second:    96864.50 [#/sec] (mean)
Time per request:       1.032 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
