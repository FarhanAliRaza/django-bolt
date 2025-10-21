"""
Python Event Loop Worker for Phase 3 Optimization

This module runs a dedicated Python event loop in a separate thread,
processing requests from Rust without blocking Actix workers.

Architecture:
- Python manages its own asyncio event loop
- Rust submits work to asyncio.Queue (non-blocking)
- Python processes requests asynchronously
- Results sent back to Rust via channels
"""

import asyncio
import sys
import traceback
from typing import Any, Dict, Callable


WORKER_LOOP: asyncio.AbstractEventLoop | None = None
REQUEST_QUEUE: asyncio.Queue | None = None

async def python_event_loop_worker(
    request_queue: asyncio.Queue,
    send_response_fn: Callable,
    handler_map: Dict[int, Callable],
    api_dispatch: Callable,
):
    """
    Dedicated Python worker that processes requests from Rust.

    Args:
        request_queue: asyncio.Queue receiving (request_id, handler_id, request_dict)
        send_response_fn: Rust function to send response back: fn(request_id, status, headers, body)
        handler_map: Map of handler_id -> handler function
        api_dispatch: BoltAPI._dispatch method
    """
    print("[django-bolt] Python event loop worker started", file=sys.stderr)
    print(f"[django-bolt] Queue type: {type(request_queue)}", file=sys.stderr)
    print(f"[django-bolt] Handler map has {len(handler_map)} handlers", file=sys.stderr)

    processed_count = 0

    while True:
        try:
            # Get request from queue (blocks until available)
            print("[django-bolt] Waiting for request from queue...", file=sys.stderr)
            request_id, handler_id, request_dict = await request_queue.get()
            print(f"[django-bolt] Received request {request_id} for handler {handler_id}", file=sys.stderr)

            try:
                # Get handler from map
                handler = handler_map.get(handler_id)
                if handler is None:
                    # Handler not found - send error response
                    error_response = (
                        500,
                        [("content-type", "application/json")],
                        b'{"detail":"Handler not found"}'
                    )
                    send_response_fn(request_id, *error_response)
                    continue

                # Execute handler via dispatch
                # api_dispatch handles all parameter binding, validation, serialization
                result = await api_dispatch(handler, request_dict, handler_id)

                # Result is (status_code, headers, body)
                if isinstance(result, tuple) and len(result) == 3:
                    status_code, headers, body = result
                    send_response_fn(request_id, status_code, headers, body)
                else:
                    # Unexpected response format
                    error_response = (
                        500,
                        [("content-type", "application/json")],
                        b'{"detail":"Invalid response format from handler"}'
                    )
                    send_response_fn(request_id, *error_response)

                processed_count += 1
                if processed_count % 1000 == 0:
                    print(f"[django-bolt] Processed {processed_count} requests", file=sys.stderr)

            except Exception as e:
                # Handler execution failed - send error response
                print(f"[django-bolt] Handler error: {e}", file=sys.stderr)
                traceback.print_exc(file=sys.stderr)

                error_msg = str(e)
                error_response = (
                    500,
                    [("content-type", "application/json")],
                    f'{{"detail":"{error_msg}"}}'.encode('utf-8')
                )
                send_response_fn(request_id, *error_response)

            finally:
                # Mark task as done
                request_queue.task_done()

        except asyncio.CancelledError:
            print("[django-bolt] Python event loop worker cancelled", file=sys.stderr)
            break
        except Exception as e:
            print(f"[django-bolt] Event loop worker error: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)


def start_event_loop_worker(
    request_queue: asyncio.Queue,
    send_response_fn: Callable,
    handler_map: Dict[int, Callable],
    api_dispatch: Callable,
):
    """
    Start the event loop worker in the current thread.
    This function blocks and runs the event loop.

    Should be called from a dedicated thread started by Rust.
    """
    # Create new event loop for this thread and record globals for cross-thread submission
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    global WORKER_LOOP, REQUEST_QUEUE
    WORKER_LOOP = loop
    REQUEST_QUEUE = request_queue

    try:
        # Run the worker coroutine
        loop.run_until_complete(
            python_event_loop_worker(
                request_queue,
                send_response_fn,
                handler_map,
                api_dispatch,
            )
        )
    except KeyboardInterrupt:
        print("[django-bolt] Event loop worker interrupted", file=sys.stderr)
    finally:
        loop.close()


def submit_from_rust(item: Any):
    """
    Thread-safe submission helper for Rust callers.
    Uses the worker's loop and queue captured at startup.
    """
    if WORKER_LOOP is None or REQUEST_QUEUE is None:
        print("[django-bolt] submit_from_rust called before worker initialized", file=sys.stderr)
        return

    async def _put():
        await REQUEST_QUEUE.put(item)

    def _schedule():
        asyncio.ensure_future(_put(), loop=WORKER_LOOP)

    WORKER_LOOP.call_soon_threadsafe(_schedule)
