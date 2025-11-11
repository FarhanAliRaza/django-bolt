# Django-Bolt Benchmark

Generated: Tue Nov 11 05:18:00 PM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance

Failed requests: 0
Requests per second: 99336.43 [#/sec] (mean)
Time per request: 1.007 [ms] (mean)
Time per request: 0.010 [ms] (mean, across all concurrent requests)

## 10kb JSON Response Performance

### 10kb JSON (Async) (/10k-json)

Failed requests: 0
Requests per second: 81361.67 [#/sec] (mean)
Time per request: 1.229 [ms] (mean)
Time per request: 0.012 [ms] (mean, across all concurrent requests)

### 10kb JSON (Sync) (/sync-10k-json)

Failed requests: 0
Requests per second: 83093.06 [#/sec] (mean)
Time per request: 1.203 [ms] (mean)
Time per request: 0.012 [ms] (mean, across all concurrent requests)

## Response Type Endpoints

### Header Endpoint (/header)

Failed requests: 0
Requests per second: 92717.93 [#/sec] (mean)
Time per request: 1.079 [ms] (mean)
Time per request: 0.011 [ms] (mean, across all concurrent requests)

### Cookie Endpoint (/cookie)

Failed requests: 0
Requests per second: 95909.46 [#/sec] (mean)
Time per request: 1.043 [ms] (mean)
Time per request: 0.010 [ms] (mean, across all concurrent requests)

### Exception Endpoint (/exc)

Failed requests: 0
Requests per second: 99276.28 [#/sec] (mean)
Time per request: 1.007 [ms] (mean)
Time per request: 0.010 [ms] (mean, across all concurrent requests)

### HTML Response (/html)

Failed requests: 0
Requests per second: 103086.41 [#/sec] (mean)
Time per request: 0.970 [ms] (mean)
Time per request: 0.010 [ms] (mean, across all concurrent requests)

### Redirect Response (/redirect)

Failed requests: 0
Requests per second: 99376.91 [#/sec] (mean)
Time per request: 1.006 [ms] (mean)
Time per request: 0.010 [ms] (mean, across all concurrent requests)

### File Static via FileResponse (/file-static)

Failed requests: 0
Requests per second: 30396.80 [#/sec] (mean)
Time per request: 3.290 [ms] (mean)
Time per request: 0.033 [ms] (mean, across all concurrent requests)

## Authentication & Authorization Performance

### Get Authenticated User (/auth/me)

Failed requests: 0
Requests per second: 15752.92 [#/sec] (mean)
Time per request: 6.348 [ms] (mean)
Time per request: 0.063 [ms] (mean, across all concurrent requests)

### Get User via Dependency (/auth/me-dependency)

Failed requests: 0
Requests per second: 8925.45 [#/sec] (mean)
Time per request: 11.204 [ms] (mean)
Time per request: 0.112 [ms] (mean, across all concurrent requests)

### Get Auth Context (/auth/context)

Failed requests: 0
Requests per second: 13170.74 [#/sec] (mean)
Time per request: 7.593 [ms] (mean)
Time per request: 0.076 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance

SEE STREAMING_BENCHMARK_DEV.md

## Items GET Performance (/items/1?q=hello)

Failed requests: 0
Requests per second: 43689.30 [#/sec] (mean)
Time per request: 2.289 [ms] (mean)
Time per request: 0.023 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)

Failed requests: 0
Requests per second: 65999.19 [#/sec] (mean)
Time per request: 1.515 [ms] (mean)
Time per request: 0.015 [ms] (mean, across all concurrent requests)

## ORM Performance

Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database

### Users Full10 (Async) (/users/full10)

Failed requests: 0
Requests per second: 15353.77 [#/sec] (mean)
Time per request: 6.513 [ms] (mean)
Time per request: 0.065 [ms] (mean, across all concurrent requests)

### Users Full10 (Sync) (/users/sync-full10)

Failed requests: 0
Requests per second: 13660.23 [#/sec] (mean)
Time per request: 7.321 [ms] (mean)
Time per request: 0.073 [ms] (mean, across all concurrent requests)

### Users Mini10 (Async) (/users/mini10)

Failed requests: 0
Requests per second: 19300.51 [#/sec] (mean)
Time per request: 5.181 [ms] (mean)
Time per request: 0.052 [ms] (mean, across all concurrent requests)

### Users Mini10 (Sync) (/users/sync-mini10)

Failed requests: 0
Requests per second: 19040.44 [#/sec] (mean)
Time per request: 5.252 [ms] (mean)
Time per request: 0.053 [ms] (mean, across all concurrent requests)
Cleaning up test users...

## Class-Based Views (CBV) Performance

### Simple APIView GET (/cbv-simple)

Failed requests: 0
Requests per second: 102667.30 [#/sec] (mean)
Time per request: 0.974 [ms] (mean)
Time per request: 0.010 [ms] (mean, across all concurrent requests)

### Simple APIView POST (/cbv-simple)

Failed requests: 0
Requests per second: 97041.21 [#/sec] (mean)
Time per request: 1.030 [ms] (mean)
Time per request: 0.010 [ms] (mean, across all concurrent requests)

### Items100 ViewSet GET (/cbv-items100)

Failed requests: 0
Requests per second: 66939.33 [#/sec] (mean)
Time per request: 1.494 [ms] (mean)
Time per request: 0.015 [ms] (mean, across all concurrent requests)

## CBV Items - Basic Operations

### CBV Items GET (Retrieve) (/cbv-items/1)

Failed requests: 0
Requests per second: 95854.30 [#/sec] (mean)
Time per request: 1.043 [ms] (mean)
Time per request: 0.010 [ms] (mean, across all concurrent requests)

### CBV Items PUT (Update) (/cbv-items/1)

Failed requests: 0
Requests per second: 93899.36 [#/sec] (mean)
Time per request: 1.065 [ms] (mean)
Time per request: 0.011 [ms] (mean, across all concurrent requests)

## CBV Additional Benchmarks

### CBV Bench Parse (POST /cbv-bench-parse)

Failed requests: 0
Requests per second: 97161.90 [#/sec] (mean)
Time per request: 1.029 [ms] (mean)
Time per request: 0.010 [ms] (mean, across all concurrent requests)

### CBV Response Types (/cbv-response)

Failed requests: 0
Requests per second: 102240.08 [#/sec] (mean)
Time per request: 0.978 [ms] (mean)
Time per request: 0.010 [ms] (mean, across all concurrent requests)

## ORM Performance with CBV

Seeding 1000 users for CBV benchmark...
Successfully seeded users
Validated: 10 users exist in database

### Users CBV Mini10 (List) (/users/cbv-mini10)

Failed requests: 0
Requests per second: 17786.41 [#/sec] (mean)
Time per request: 5.622 [ms] (mean)
Time per request: 0.056 [ms] (mean, across all concurrent requests)
Cleaning up test users...

## Form and File Upload Performance

### Form Data (POST /form)

Failed requests: 0
Requests per second: 78245.42 [#/sec] (mean)
Time per request: 1.278 [ms] (mean)
Time per request: 0.013 [ms] (mean, across all concurrent requests)

### File Upload (POST /upload)

Failed requests: 0
Requests per second: 60822.07 [#/sec] (mean)
Time per request: 1.644 [ms] (mean)
Time per request: 0.016 [ms] (mean, across all concurrent requests)

### Mixed Form with Files (POST /mixed-form)

Failed requests: 0
Requests per second: 57309.22 [#/sec] (mean)
Time per request: 1.745 [ms] (mean)
Time per request: 0.017 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks

### JSON Parse/Validate (POST /bench/parse)

Failed requests: 0
Requests per second: 94085.77 [#/sec] (mean)
Time per request: 1.063 [ms] (mean)
Time per request: 0.011 [ms] (mean, across all concurrent requests)
