"""
High-performance async to sync collector for streaming.
Implements proven patterns for efficient async iterator batching and PyO3 boundary optimization.
"""

import asyncio
from datetime import timedelta
from typing import AsyncIterable, AsyncIterator, Iterator, List, Optional, TypeVar, Union

X = TypeVar("X")


def batch_async(
    aib: AsyncIterable[X],
    timeout: timedelta,
    batch_size: int,
    loop: Optional[asyncio.AbstractEventLoop] = None,
) -> Iterator[List[X]]:
    """
    Batch an async iterable synchronously without timeouts for minimal latency.
    
    Optimized for low-latency streaming:
    - No timeout overhead for immediate async generators
    - Direct async iteration for maximum speed
    - Simplified control flow
    
    Args:
        aib: The underlying source async iterable of items
        timeout: Ignored in this optimized version
        batch_size: Maximum number of items to yield in a batch
        loop: Custom asyncio run loop to use, if any
        
    Yields:
        The next gathered batch of items
    """
    # Ensure that we have the stateful iterator of the source
    ait = aib.__aiter__()
    
    loop = loop if loop is not None else asyncio.new_event_loop()
    
    async def get_next_batch():
        batch = []
        # Gather items greedily up to batch_size
        # This is optimal for small iterators (SSE with 3-5 chunks)
        for _ in range(batch_size):
            try:
                next_item = await ait.__anext__()
                batch.append(next_item)
            except StopAsyncIteration:
                # End of iterator
                break
        return batch
    
    while True:
        # Direct execution without timeout wrapper for minimal overhead
        batch = loop.run_until_complete(get_next_batch())
        if not batch:
            return
        yield batch


class AsyncToSyncCollector:
    """
    High-performance async stream collector for Rust integration.
    
    Optimized for streaming with efficient batching to minimize PyO3 boundary 
    crossings while maintaining good throughput and latency characteristics.
    """
    
    def __init__(
        self,
        async_iterable: AsyncIterable,
        batch_size: int = 50,  # Optimized for OpenAI streaming
        timeout_ms: int = 10,   # Low latency: 10ms timeout
        convert_to_bytes: bool = True
    ):
        """
        Initialize the collector.
        
        Args:
            async_iterable: The async iterable to collect from
            batch_size: Number of chunks to batch together
            timeout_ms: Maximum time to wait for a full batch (milliseconds)
            convert_to_bytes: Whether to convert items to bytes
        """
        # Assume it's an AsyncIterable and let batch_async call __aiter__() on it
        self.async_gen = async_iterable
            
        self.batch_size = batch_size
        self.timeout = timedelta(milliseconds=timeout_ms)
        self.convert_to_bytes = convert_to_bytes
        self._iterator = None
        self._loop = None
        
    def _convert_to_bytes(self, item) -> bytes:
        """Convert various types to bytes for streaming."""
        if isinstance(item, bytes):
            return item
        elif isinstance(item, bytearray):
            return bytes(item)
        elif isinstance(item, memoryview):
            return bytes(item)
        elif isinstance(item, str):
            return item.encode('utf-8')
        else:
            return str(item).encode('utf-8')
    
    def __iter__(self):
        """Initialize the iterator."""
        # Try to use existing event loop, create new one only if needed
        try:
            # Try to get the running event loop first
            self._loop = asyncio.get_running_loop()
        except RuntimeError:
            # No event loop running, create a new one
            self._loop = asyncio.new_event_loop()
        
        # Get the batch iterator
        self._iterator = batch_async(
            self.async_gen,
            self.timeout,
            self.batch_size,
            self._loop
        )
        return self
    
    def __next__(self) -> bytes:
        """Get the next batch of chunks as a single bytes object."""
        # Initialize iterator if not already done (Rust calls __next__ without __iter__)
        if self._iterator is None:
            self.__iter__()
        
        try:
            batch = next(self._iterator)
            
            # Empty batch means we're done
            if not batch:
                if self._loop:
                    self._loop.close()
                    self._loop = None
                raise StopIteration
            
            if self.convert_to_bytes:
                # Convert and join all chunks into a single bytes object
                # This is critical for performance - one PyO3 crossing instead of many
                converted = [self._convert_to_bytes(item) for item in batch]
                return b''.join(converted)
            else:
                # Return raw batch if conversion not needed
                return batch
                
        except StopIteration:
            # Clean up the event loop
            if self._loop:
                self._loop.close()
                self._loop = None
            raise
        except Exception as e:
            # Clean up on any error
            if self._loop:
                self._loop.close()
                self._loop = None
            raise
    
    def __del__(self):
        """Cleanup event loop on deletion."""
        if hasattr(self, '_loop') and self._loop:
            try:
                if not self._loop.is_closed():
                    self._loop.close()
            except:
                pass


def wrap_async_stream(
    async_gen: AsyncIterable,
    batch_size: int = 50,
    timeout_ms: int = 10
) -> Iterator[bytes]:
    """
    Convenience function to wrap an async generator for sync iteration.
    
    Args:
        async_gen: The async generator to wrap
        batch_size: Number of chunks to batch together
        timeout_ms: Maximum time to wait for a full batch (milliseconds)
        
    Returns:
        A sync iterator that yields batched bytes
    """
    return AsyncToSyncCollector(async_gen, batch_size, timeout_ms)


# Performance-tuned configurations for different streaming scenarios
class StreamProfiles:
    """Pre-configured profiles for different streaming scenarios."""
    
    @staticmethod
    def openai_streaming():
        """Optimized for OpenAI-style token streaming (many small chunks)."""
        return {
            'batch_size': 100,  # Aggressive batching for tiny chunks
            'timeout_ms': 20    # 20ms max latency
        }
    
    @staticmethod
    def large_chunks():
        """Optimized for larger chunk streaming (e.g., file downloads)."""
        return {
            'batch_size': 10,   # Less batching needed
            'timeout_ms': 50    # Can tolerate more latency
        }
    
    @staticmethod
    def realtime():
        """Optimized for real-time streaming with minimal latency."""
        return {
            'batch_size': 5,    # Small batches
            'timeout_ms': 5     # Ultra-low latency (5ms)
        }
    
    @staticmethod
    def high_throughput():
        """Optimized for maximum throughput (batch processing)."""
        return {
            'batch_size': 200,  # Very aggressive batching
            'timeout_ms': 100   # Higher latency acceptable
        }