#!/usr/bin/env python3
"""
SSE Load Test Script
Measures real SSE streaming performance with concurrent clients.
"""
from __future__ import annotations

import argparse
import asyncio
import contextlib
import os
import sys
import time
from datetime import datetime
from statistics import mean, stdev

import aiohttp
import psutil


class SSELoadTest:
    def __init__(self, url: str, num_clients: int = 10, duration: int = 30, batch_size: int = 10):
        self.url = url
        self.num_clients = num_clients
        self.duration = duration
        self.batch_size = batch_size
        self.results = []
        self.start_time = None
        self.process = psutil.Process(os.getpid())
        self.cpu_samples = []  # Track CPU samples during test

    async def sse_client(self, client_id: int) -> dict:
        """Simulate one SSE client holding connection open"""
        client_start = time.time()
        messages = 0
        bytes_received = 0
        error = None

        try:
            # print(f"    Client {client_id}: Connecting...", flush=True)
            async with (
                aiohttp.ClientSession() as session,
                session.get(self.url, timeout=aiohttp.ClientTimeout(total=None)) as resp,
            ):
                # print(f"    Client {client_id}: Connected (status {resp.status})", flush=True)
                if resp.status != 200:
                    return {
                        "client_id": client_id,
                        "status": "failed",
                        "error": f"HTTP {resp.status}",
                        "messages": 0,
                        "bytes": 0,
                        "duration": 0,
                    }

                # Stream until duration exceeded or connection closes
                # Add timeout to prevent hanging if chunks don't arrive
                async def stream() -> None:
                    nonlocal messages, bytes_received
                    async for chunk in resp.content.iter_any():
                        elapsed = time.time() - client_start
                        if elapsed > self.duration:
                            break

                        if chunk:
                            messages += 1
                            bytes_received += len(chunk)

                # Duration exceeded, stop streaming
                with contextlib.suppress(asyncio.TimeoutError):
                    await asyncio.wait_for(stream(), timeout=self.duration + 5)

        except TimeoutError:
            error = "Timeout"
        except aiohttp.ClientError as e:
            error = f"Connection error: {str(e)[:50]}"
        except Exception as e:
            error = f"Error: {str(e)[:50]}"

        elapsed = time.time() - client_start
        status = "failed" if error else "success"
        print(f"    Client {client_id}: {status} ({messages} msgs, {elapsed:.1f}s){f' - {error}' if error else ''}", flush=True)

        return {
            "client_id": client_id,
            "status": "success" if not error else "failed",
            "error": error,
            "messages": messages,
            "bytes": bytes_received,
            "duration": elapsed,
        }

    def get_system_stats(self) -> dict:
        """Get current process resource usage"""
        try:
            mem_info = self.process.memory_info()
            # Use interval=0 to get instantaneous CPU usage (non-blocking)
            return {
                "memory_mb": mem_info.rss / 1024 / 1024,
                "cpu_percent": self.process.cpu_percent(interval=0),
            }
        except Exception:
            return {"memory_mb": 0, "cpu_percent": 0}

    async def _sample_cpu_during_batch(self, duration: float) -> None:
        """Sample CPU usage every 0.1s for the given duration"""
        start = time.time()
        while time.time() - start < duration:
            self.cpu_samples.append(self.process.cpu_percent(interval=0))
            await asyncio.sleep(0.1)

    async def run(self) -> None:
        """Run the load test"""
        print(f"\n{'='*70}")
        print("SSE Load Test")
        print(f"{'='*70}")
        print(f"URL: {self.url}")
        print(f"Concurrent Clients: {self.num_clients}")
        print(f"Duration per Client: {self.duration}s")
        print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}\n")

        self.start_time = time.time()

        # Print progress
        print("Launching clients...\n")
        for i in range(0, self.num_clients, self.batch_size):
            batch_size = min(self.batch_size, self.num_clients - i)
            print(f"  [{i:4d}/{self.num_clients}] Launching {batch_size} clients...")

            # Launch in batches to avoid overwhelming the system
            tasks = [self.sse_client(j) for j in range(i, i + batch_size)]
            print(f"  Waiting for {len(tasks)} clients to connect and run for {self.duration}s...", flush=True)

            # Run batch tasks and CPU sampling concurrently
            batch_tasks = asyncio.gather(*tasks)
            cpu_sampler = self._sample_cpu_during_batch(self.duration + 5)  # Sample until after clients finish

            batch_results, _ = await asyncio.gather(batch_tasks, cpu_sampler)
            self.results.extend(batch_results)

            elapsed = time.time() - self.start_time
            sys_stats = self.get_system_stats()
            print(f"  Batch complete ({elapsed:.1f}s, {sys_stats['memory_mb']:.1f}MB, CPU: {sys_stats['cpu_percent']:.1f}%)\n")

        total_time = time.time() - self.start_time
        print(f"\nTest completed in {total_time:.2f}s")
        print()

        # Print detailed results
        self._print_results()

    def _print_results(self) -> None:
        """Print and analyze results"""
        successful = [r for r in self.results if r["status"] == "success"]
        failed = [r for r in self.results if r["status"] == "failed"]

        print(f"{'='*70}")
        print("RESULTS")
        print(f"{'='*70}\n")

        # Summary
        print(f"Total Clients: {self.num_clients}")
        print(f"Successful: {len(successful)} ({len(successful)/self.num_clients*100:.1f}%)")
        print(f"Failed: {len(failed)} ({len(failed)/self.num_clients*100:.1f}%)")

        if failed:
            print("\nFailure Details:")
            for r in failed[:5]:  # Show first 5 failures
                print(f"  Client {r['client_id']}: {r['error']}")
            if len(failed) > 5:
                print(f"  ... and {len(failed)-5} more failures")

        print()

        if successful:
            # Message delivery stats
            messages_list = [r["messages"] for r in successful]
            bytes_list = [r["bytes"] for r in successful]
            duration_list = [r["duration"] for r in successful]

            print("Message Delivery:")
            print(f"  Total Messages: {sum(messages_list):,}")
            print(f"  Avg Messages/Client: {mean(messages_list):.1f}")
            if len(messages_list) > 1:
                print(f"  StDev: {stdev(messages_list):.1f}")
            print(f"  Min/Max: {min(messages_list)}/{max(messages_list)}")

            print("\nData Transfer:")
            print(f"  Total Bytes: {sum(bytes_list):,} ({sum(bytes_list)/1024/1024:.2f} MB)")
            print(f"  Avg Bytes/Client: {mean(bytes_list):,.0f}")
            total_duration = sum(duration_list)
            if total_duration > 0:
                print(f"  Throughput: {sum(bytes_list)/total_duration/1024/1024:.2f} MB/s")

            print("\nConnection Duration:")
            print(f"  Avg Duration: {mean(duration_list):.2f}s")
            if len(duration_list) > 1:
                print(f"  StDev: {stdev(duration_list):.2f}s")
            print(f"  Min/Max: {min(duration_list):.2f}s / {max(duration_list):.2f}s")

            print("\nMessaging Rate:")
            avg_rate = mean([m / d for m, d in zip(messages_list, duration_list, strict=True)])
            print(f"  Avg Messages/sec/client: {avg_rate:.2f}")
            print(f"  Total Messages/sec: {sum(messages_list)/mean(duration_list):.2f}")

        print()

        # Resource usage
        sys_stats = self.get_system_stats()
        avg_cpu = mean(self.cpu_samples) if self.cpu_samples else 0
        print("Resource Usage:")
        print(f"  Memory: {sys_stats['memory_mb']:.1f} MB")
        print(f"  CPU (current): {sys_stats['cpu_percent']:.1f}%")
        if self.cpu_samples:
            print(f"  CPU (avg during test): {avg_cpu:.1f}%")
            print(f"  CPU (min/max during test): {min(self.cpu_samples):.1f}% / {max(self.cpu_samples):.1f}%")

        print()
        print(f"{'='*70}\n")


async def main() -> None:
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="SSE Load Test - Measures concurrent SSE streaming performance"
    )
    parser.add_argument(
        "url",
        nargs="?",
        default="http://127.0.0.1:8000/sse",
        help="URL of SSE endpoint (default: http://127.0.0.1:8000/sse)"
    )
    parser.add_argument(
        "-c", "--clients",
        type=int,
        default=50,
        help="Number of concurrent clients (default: 50)"
    )
    parser.add_argument(
        "-d", "--duration",
        type=int,
        default=30,
        help="Duration per client in seconds (default: 30)"
    )
    parser.add_argument(
        "-b", "--batch-size",
        type=int,
        default=10,
        help="Launch batch size (default: 10, use -1 for all at once)"
    )

    args = parser.parse_args()

    # If batch_size is -1, launch all at once
    if args.batch_size == -1:
        args.batch_size = args.clients

    # Validate URL
    if not args.url.startswith("http"):
        print(f"Error: Invalid URL '{args.url}'. Must start with http:// or https://")
        sys.exit(1)

    # Run test
    test = SSELoadTest(
        args.url,
        num_clients=args.clients,
        duration=args.duration,
        batch_size=args.batch_size
    )
    await test.run()


if __name__ == "__main__":
    asyncio.run(main())
