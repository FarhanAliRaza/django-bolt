# Django-Bolt Benchmark
Generated: Sun Nov  9 01:58:02 UTC 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance

## 10kb JSON Response Performance
### 10kb JSON (Async) (/10k-json)
### 10kb JSON (Sync) (/sync-10k-json)

## Response Type Endpoints
### Header Endpoint (/header)
### Cookie Endpoint (/cookie)
### Exception Endpoint (/exc)
### HTML Response (/html)
### Redirect Response (/redirect)
### File Static via FileResponse (/file-static)

## Streaming and SSE Performance
SEE STREAMING_BENCHMARK_DEV.md

## Items GET Performance (/items/1?q=hello)

## Items PUT JSON Performance (/items/1)

## ORM Performance
Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users Full10 (Async) (/users/full10)
### Users Full10 (Sync) (/users/sync-full10)
### Users Mini10 (Async) (/users/mini10)
### Users Mini10 (Sync) (/users/sync-mini10)
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
### Simple APIView POST (/cbv-simple)
### Items100 ViewSet GET (/cbv-items100)

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
### CBV Items PUT (Update) (/cbv-items/1)

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
### CBV Response Types (/cbv-response)

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users CBV Mini10 (List) (/users/cbv-mini10)
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
### File Upload (POST /upload)
### Mixed Form with Files (POST /mixed-form)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
