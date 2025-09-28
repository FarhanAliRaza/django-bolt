#!/usr/bin/env python3
"""Test the AsyncToSyncCollector directly."""

import asyncio
from django_bolt.async_collector import AsyncToSyncCollector

async def test_generator():
    """Simple async generator for testing."""
    for i in range(3):
        yield f"chunk {i}\n".encode()
    print("Generator completed")

# Create async generator
agen = test_generator()

# Wrap with collector
collector = AsyncToSyncCollector(agen, batch_size=2)

# Test iteration
print("Starting iteration...")
for i, chunk in enumerate(collector):
    print(f"Got chunk {i}: {chunk!r}")

print("Done!")