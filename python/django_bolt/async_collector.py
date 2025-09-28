"""
Async to Sync Collector for bypassing PyO3 async bridge.
This runs Python async iteration in its own thread and provides sync interface to Rust.
"""

import asyncio
import threading
import queue
from typing import AsyncIterator, Iterator, Any


class AsyncToSyncCollector:
    """
    Collects async generator output in Python thread, provides sync iterator to Rust.
    This completely bypasses the PyO3 async bridge overhead.
    """
    
    def __init__(self, async_gen: AsyncIterator, batch_size: int = 20, prefetch: int = 100, start_immediately: bool = True):
        """
        Initialize the collector.
        
        Args:
            async_gen: The async generator to collect from
            batch_size: Number of chunks to batch together (reduces overhead)
            prefetch: Maximum queue size for prefetching
            start_immediately: Start collection thread immediately (needed for Rust integration)
        """
        self.async_gen = async_gen
        self.batch_size = batch_size
        self.queue = queue.Queue(maxsize=prefetch)
        self.thread = None
        self.done = False
        self.exception = None
        self._started = False
        
        if start_immediately:
            # Start thread immediately for Rust integration
            # This avoids deadlock with spawn_blocking
            self._start_thread()
        
    def _run_async(self):
        """Run async collection in separate thread with dedicated event loop."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self._collect())
        except Exception as e:
            self.exception = e
        finally:
            self.done = True
            # Put sentinel to unblock any waiting __next__ calls
            try:
                self.queue.put(None, block=False)
            except queue.Full:
                pass
            loop.close()
        
    async def _collect(self):
        """Collect chunks from async generator and batch them."""
        batch = []
        try:
            async for chunk in self.async_gen:
                # Convert various types to bytes
                if isinstance(chunk, bytes):
                    batch.append(chunk)
                elif isinstance(chunk, bytearray):
                    batch.append(bytes(chunk))
                elif isinstance(chunk, memoryview):
                    batch.append(bytes(chunk))
                elif hasattr(chunk, 'encode'):
                    # String-like objects
                    batch.append(chunk.encode())
                else:
                    # Fallback: convert to string then bytes
                    batch.append(str(chunk).encode())
                
                # Send batch when full
                if len(batch) >= self.batch_size:
                    # Join into single bytes object for efficiency
                    combined = b"".join(batch)
                    self.queue.put(combined)
                    batch = []
            
            # Send remaining batch
            if batch:
                combined = b"".join(batch)
                self.queue.put(combined)
                
        except StopAsyncIteration:
            # Normal completion
            if batch:
                combined = b"".join(batch)
                self.queue.put(combined)
        except Exception as e:
            # Store exception to re-raise in sync context
            self.exception = e
            raise
    
    def _start_thread(self):
        """Start the collection thread."""
        if not self._started:
            self._started = True
            self.thread = threading.Thread(target=self._run_async, daemon=True)
            self.thread.start()
    
    def __iter__(self):
        """Return self as iterator, start collection thread if needed."""
        self._start_thread()  # Ensure thread is started
        return self
        
    def __next__(self):
        """Get next chunk synchronously."""
        # Check for exceptions from async thread
        if self.exception:
            raise self.exception
            
        # Check if done and queue is empty
        if self.done and self.queue.empty():
            raise StopIteration
            
        try:
            # Get from queue with timeout
            item = self.queue.get(timeout=30)
            
            # Check for sentinel (None means done)
            if item is None:
                raise StopIteration
                
            return item
            
        except queue.Empty:
            if self.done:
                raise StopIteration
            # Timeout without completion - something is wrong
            raise RuntimeError("Async collection timeout - generator may be stuck")


def wrap_async_generator(async_gen: AsyncIterator, batch_size: int = 20) -> Iterator:
    """
    Convenience function to wrap an async generator for sync iteration.
    
    Args:
        async_gen: The async generator to wrap
        batch_size: Number of chunks to batch together
        
    Returns:
        A sync iterator that yields the async generator's output
    """
    return AsyncToSyncCollector(async_gen, batch_size=batch_size)