#!/usr/bin/env python
"""
Blog Homepage Performance Comparison Benchmark

Compares performance of:
1. Traditional Django + Gunicorn (WSGI) - /blog/
2. Django-Bolt (ASGI + Rust) - /blog

This benchmark tests a realistic scenario: rendering an HTML page with database
queries for blog data and styling with Tailwind CSS.

Usage:
    # Start django-bolt server
    python manage.py runbolt --host 127.0.0.1 --port 8000

    # In another terminal, run this benchmark
    python bench_blog_performance.py
"""

import httpx
import time
import statistics
from typing import List, Tuple
import sys


class BlogBenchmark:
    def __init__(self, bolt_url: str = "http://127.0.0.1:8000", gunicorn_url: str = "http://127.0.0.1:8001"):
        self.bolt_url = bolt_url
        self.gunicorn_url = gunicorn_url
        self.bolt_times: List[float] = []
        self.gunicorn_times: List[float] = []

    def benchmark_endpoint(self, url: str, name: str, num_requests: int = 100, concurrent: int = 10) -> Tuple[float, float, float]:
        """
        Benchmark an endpoint with concurrent requests.

        Returns (min_ms, median_ms, max_ms)
        """
        print(f"\n{'='*70}")
        print(f"Benchmarking: {name}")
        print(f"URL: {url}")
        print(f"Requests: {num_requests}, Concurrent: {concurrent}")
        print(f"{'='*70}")

        times = []

        with httpx.Client(http2=True, limits=httpx.Limits(max_connections=concurrent)) as client:
            for i in range(num_requests):
                try:
                    start = time.perf_counter()
                    response = client.get(url, timeout=30.0)
                    elapsed = (time.perf_counter() - start) * 1000  # Convert to ms

                    if response.status_code == 200:
                        times.append(elapsed)
                        if (i + 1) % 20 == 0:
                            print(f"  Progress: {i + 1}/{num_requests} requests completed")
                    else:
                        print(f"  ⚠ Request {i + 1} returned status {response.status_code}")

                except Exception as e:
                    print(f"  ❌ Request {i + 1} failed: {str(e)}")

        if not times:
            print(f"❌ No successful requests")
            return 0, 0, 0

        min_time = min(times)
        max_time = max(times)
        median_time = statistics.median(times)
        mean_time = statistics.mean(times)
        stdev = statistics.stdev(times) if len(times) > 1 else 0

        print(f"\nResults ({len(times)} successful requests):")
        print(f"  Min:      {min_time:.2f} ms")
        print(f"  Median:   {median_time:.2f} ms")
        print(f"  Mean:     {mean_time:.2f} ms")
        print(f"  Max:      {max_time:.2f} ms")
        print(f"  Std Dev:  {stdev:.2f} ms")
        print(f"  Requests/sec: {len(times) / (sum(times) / 1000 / len(times)):.2f}")

        return min_time, median_time, max_time

    def run_comparison(self, num_requests: int = 100):
        """Run full comparison benchmark."""
        print("\n" + "="*70)
        print("Blog Homepage Performance Comparison")
        print("="*70)
        print(f"Testing: Django-Bolt vs Gunicorn")
        print(f"Total requests per endpoint: {num_requests}")
        print("="*70)

        # Benchmark Django-Bolt
        print("\n[1/2] Testing Django-Bolt (ASGI + Rust)...")
        bolt_min, bolt_median, bolt_max = self.benchmark_endpoint(
            f"{self.bolt_url}/blog",
            "Django-Bolt Blog Homepage",
            num_requests=num_requests
        )

        # Note: Gunicorn benchmark requires separate setup
        print("\n" + "="*70)
        print("⚠ Note: To benchmark Gunicorn, start it separately:")
        print("  gunicorn testproject.wsgi:application --workers 2 --threads 4 --port 8001")
        print("="*70)

        try:
            print("\n[2/2] Testing Gunicorn (WSGI)...")
            gunicorn_min, gunicorn_median, gunicorn_max = self.benchmark_endpoint(
                f"{self.gunicorn_url}/blog/",
                "Gunicorn + Django Blog Homepage",
                num_requests=num_requests
            )
        except Exception as e:
            print(f"\n⚠ Gunicorn benchmark skipped: {str(e)}")
            print("  Make sure Gunicorn is running on port 8001")
            gunicorn_min = gunicorn_median = gunicorn_max = 0

        # Display comparison
        print("\n" + "="*70)
        print("PERFORMANCE COMPARISON RESULTS")
        print("="*70)
        print(f"\n{'Metric':<20} {'Django-Bolt':<20} {'Gunicorn':<20} {'Improvement':<20}")
        print("-"*80)

        if gunicorn_median > 0:
            bolt_improvement = ((gunicorn_median - bolt_median) / gunicorn_median) * 100
            speedup = gunicorn_median / bolt_median if bolt_median > 0 else 0

            print(f"{'Min (ms)':<20} {bolt_min:<20.2f} {gunicorn_min:<20.2f} {((gunicorn_min - bolt_min) / gunicorn_min * 100):<20.1f}%")
            print(f"{'Median (ms)':<20} {bolt_median:<20.2f} {gunicorn_median:<20.2f} {bolt_improvement:<20.1f}%")
            print(f"{'Max (ms)':<20} {bolt_max:<20.2f} {gunicorn_max:<20.2f} {((gunicorn_max - bolt_max) / gunicorn_max * 100):<20.1f}%")
            print(f"{'Speedup':<20} {'1.0x':<20} {f'{speedup:.1f}x':<20} {'':<20}")
        else:
            print(f"{'Median (ms)':<20} {bolt_median:<20.2f} {'N/A':<20} {'N/A':<20}")

        print("="*70)

        # Analysis
        print("\nAnalysis:")
        print(f"  - Django-Bolt serves the blog homepage via ASGI with Rust acceleration")
        print(f"  - Gunicorn serves via WSGI with traditional Python threads/workers")
        print(f"  - Both endpoints query 50 blog posts from SQLite database")
        print(f"  - Response is rendered HTML with Tailwind CSS styling")
        print(f"  - Django-Bolt uses async/await for non-blocking I/O")

        if gunicorn_median > 0 and bolt_median > 0:
            speedup = gunicorn_median / bolt_median
            print(f"\n✓ Django-Bolt is {speedup:.1f}x faster than Gunicorn for this workload")
        else:
            print("\n⚠ Could not complete full comparison. Ensure both servers are running.")


def main():
    # Parse arguments
    bolt_port = 8000
    gunicorn_port = 8001
    num_requests = 100

    if len(sys.argv) > 1:
        try:
            num_requests = int(sys.argv[1])
        except ValueError:
            print(f"Usage: {sys.argv[0]} [num_requests]")
            sys.exit(1)

    benchmark = BlogBenchmark(
        bolt_url=f"http://127.0.0.1:{bolt_port}",
        gunicorn_url=f"http://127.0.0.1:{gunicorn_port}"
    )

    try:
        benchmark.run_comparison(num_requests=num_requests)
    except KeyboardInterrupt:
        print("\n\n⚠ Benchmark interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Benchmark failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
