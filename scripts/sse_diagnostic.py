#!/usr/bin/env python3
"""
SSE Diagnostic Test - Detailed analysis of streaming behavior.
Tests a small number of concurrent clients and shows detailed timing.
"""
from __future__ import annotations

import asyncio
import aiohttp
import time
import sys
import os
from datetime import datetime


class SSEDiagnostic:
    def __init__(self, url: str, num_clients: int = 5, duration: int = 15):
        self.url = url
        self.num_clients = num_clients
        self.duration = duration
        self.results = []

    async def sse_client(self, client_id: int) -> dict:
        """Simulate one SSE client with detailed message timing."""
        client_start = time.time()
        messages = []
        error = None

        try:
            print(f"[{client_id:2d}] Connecting to {self.url}...", flush=True)
            async with aiohttp.ClientSession() as session:
                async with session.get(self.url, timeout=aiohttp.ClientTimeout(total=None)) as resp:
                    if resp.status != 200:
                        return {
                            "client_id": client_id,
                            "status": "failed",
                            "error": f"HTTP {resp.status}",
                            "messages": [],
                        }

                    print(f"[{client_id:2d}] Connected (status {resp.status}), waiting for messages...", flush=True)

                    # Stream until duration exceeded
                    async for chunk in resp.content.iter_any():
                        elapsed = time.time() - client_start
                        if elapsed > self.duration:
                            break

                        if chunk:
                            msg_time = elapsed
                            messages.append((msg_time, chunk))
                            chunk_preview = chunk[:50] if len(chunk) > 50 else chunk
                            print(f"[{client_id:2d}] {elapsed:6.2f}s: {chunk_preview}", flush=True)

        except asyncio.TimeoutError:
            error = "Timeout"
        except aiohttp.ClientError as e:
            error = f"Connection error: {str(e)[:50]}"
        except Exception as e:
            error = f"Error: {str(e)[:50]}"

        elapsed = time.time() - client_start
        status = "failed" if error else "success"

        if error:
            print(f"[{client_id:2d}] {status} - {error} ({len(messages)} msgs, {elapsed:.2f}s)", flush=True)
        else:
            print(f"[{client_id:2d}] {status} ({len(messages)} msgs, {elapsed:.2f}s)", flush=True)

        return {
            "client_id": client_id,
            "status": status,
            "error": error,
            "messages": messages,
            "total_duration": elapsed,
        }

    async def run(self) -> None:
        """Run the diagnostic test."""
        print(f"\n{'='*70}")
        print(f"SSE Diagnostic Test")
        print(f"{'='*70}")
        print(f"URL: {self.url}")
        print(f"Concurrent Clients: {self.num_clients}")
        print(f"Duration per Client: {self.duration}s")
        print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}\n")

        start_time = time.time()

        # Launch all clients concurrently
        print(f"Launching {self.num_clients} clients...\n")
        tasks = [self.sse_client(i) for i in range(self.num_clients)]
        self.results = await asyncio.gather(*tasks)

        total_time = time.time() - start_time
        print(f"\n\nTest completed in {total_time:.2f}s")
        print(f"\n{'='*70}")
        print("ANALYSIS")
        print(f"{'='*70}\n")

        # Analyze results
        successful = [r for r in self.results if r["status"] == "success"]

        if successful:
            msg_counts = [len(r["messages"]) for r in successful]
            durations = [r["total_duration"] for r in successful]

            print(f"Total Clients: {self.num_clients}")
            print(f"Successful: {len(successful)} ({len(successful)/self.num_clients*100:.1f}%)")
            print()

            print("Message Delivery:")
            print(f"  Avg Messages/Client: {sum(msg_counts)/len(msg_counts):.2f}")
            print(f"  Min/Max: {min(msg_counts)}/{max(msg_counts)}")
            print(f"  Distribution: {msg_counts}")
            print()

            print("Connection Duration:")
            print(f"  Avg: {sum(durations)/len(durations):.2f}s")
            print(f"  Min/Max: {min(durations):.2f}s / {max(durations):.2f}s")
            print(f"  Distribution: {[f'{d:.2f}s' for d in durations]}")
            print()

            # Analyze message timing patterns
            print("Message Timing Analysis:")
            for result in successful:
                client_id = result["client_id"]
                messages = result["messages"]
                if messages:
                    print(f"  Client {client_id}:")
                    intervals = []
                    for i, (msg_time, chunk) in enumerate(messages):
                        if i == 0:
                            print(f"    First: {msg_time:.2f}s")
                        else:
                            interval = msg_time - messages[i-1][0]
                            intervals.append(interval)

                    if intervals:
                        avg_interval = sum(intervals) / len(intervals)
                        print(f"    Avg Interval: {avg_interval:.2f}s (expected ~2.0s)")
                        print(f"    Intervals: {[f'{i:.2f}s' for i in intervals]}")

        print()
        print(f"{'='*70}\n")


async def main() -> None:
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="SSE Diagnostic - Detailed analysis of streaming behavior"
    )
    parser.add_argument(
        "url",
        nargs="?",
        default="http://127.0.0.1:8000/sync-sse",
        help="URL of SSE endpoint (default: http://127.0.0.1:8000/sync-sse)"
    )
    parser.add_argument(
        "-c", "--clients",
        type=int,
        default=5,
        help="Number of concurrent clients (default: 5)"
    )
    parser.add_argument(
        "-d", "--duration",
        type=int,
        default=15,
        help="Duration per client in seconds (default: 15)"
    )

    args = parser.parse_args()

    # Validate URL
    if not args.url.startswith("http"):
        print(f"Error: Invalid URL '{args.url}'. Must start with http:// or https://")
        sys.exit(1)

    # Run diagnostic
    diagnostic = SSEDiagnostic(
        args.url,
        num_clients=args.clients,
        duration=args.duration
    )
    await diagnostic.run()


if __name__ == "__main__":
    asyncio.run(main())
