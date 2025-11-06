"""
Test sync function support in django-bolt.
This file tests that the Python side correctly detects and handles sync functions.
"""
from django_bolt import BoltAPI
import inspect

api = BoltAPI()

# Test 1: Async function (existing behavior)
@api.get("/async", inline=True)
async def async_handler():
    return {"type": "async"}

# Test 2: Sync function with inline=True (default)
@api.get("/sync-inline")
def sync_inline_handler():
    return {"type": "sync", "mode": "inline"}

# Test 3: Sync function with inline=False (spawn_blocking)
@api.get("/sync-blocking", inline=False)
def sync_blocking_handler():
    import time
    time.sleep(0.001)  # Simulate slow operation
    return {"type": "sync", "mode": "blocking"}

# Test 4: Verify metadata
print("Testing metadata detection...")

# Check async handler
async_meta = api._handler_meta[async_handler]
print(f"✓ Async handler metadata:")
print(f"  - is_async: {async_meta['is_async']} (expected: True)")
print(f"  - inline: {async_meta['inline']} (expected: True)")
assert async_meta['is_async'] == True
assert async_meta['inline'] == True

# Check sync inline handler
sync_inline_meta = api._handler_meta[sync_inline_handler]
print(f"\n✓ Sync inline handler metadata:")
print(f"  - is_async: {sync_inline_meta['is_async']} (expected: False)")
print(f"  - inline: {sync_inline_meta['inline']} (expected: True)")
assert sync_inline_meta['is_async'] == False
assert sync_inline_meta['inline'] == True

# Check sync blocking handler
sync_blocking_meta = api._handler_meta[sync_blocking_handler]
print(f"\n✓ Sync blocking handler metadata:")
print(f"  - is_async: {sync_blocking_meta['is_async']} (expected: False)")
print(f"  - inline: {sync_blocking_meta['inline']} (expected: False)")
assert sync_blocking_meta['is_async'] == False
assert sync_blocking_meta['inline'] == False

print("\n✅ All metadata tests passed!")

# Test 5: Verify handlers are callable
print("\nTesting handler execution...")

# Async handler should be a coroutine function
assert inspect.iscoroutinefunction(async_handler)
print(f"✓ Async handler is coroutine function: {inspect.iscoroutinefunction(async_handler)}")

# Sync handlers should not be coroutine functions
assert not inspect.iscoroutinefunction(sync_inline_handler)
print(f"✓ Sync inline handler is NOT coroutine function: {not inspect.iscoroutinefunction(sync_inline_handler)}")

assert not inspect.iscoroutinefunction(sync_blocking_handler)
print(f"✓ Sync blocking handler is NOT coroutine function: {not inspect.iscoroutinefunction(sync_blocking_handler)}")

print("\n✅ All tests passed! Sync function support is working correctly on the Python side.")
print("\nNote: Full integration testing requires building the Rust extension.")
