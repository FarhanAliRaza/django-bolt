"""
Lifecycle hooks for Django-Bolt API.

Provides startup and shutdown event handlers similar to FastAPI's on_event system.
Hooks are executed before server starts (startup) and after server stops (shutdown).

Usage:
    from django_bolt import BoltAPI

    api = BoltAPI()

    @api.on_startup
    async def startup():
        print("Server starting...")
        # Initialize database connections, load ML models, etc.

    @api.on_shutdown
    async def shutdown():
        print("Server shutting down...")
        # Close connections, cleanup resources, etc.

Both sync and async handlers are supported:

    @api.on_startup
    def sync_startup():
        print("Sync startup handler")

    @api.on_startup
    async def async_startup():
        print("Async startup handler")
"""

from __future__ import annotations

import asyncio
import inspect
import logging
from collections.abc import Callable
from typing import Any

logger = logging.getLogger("django_bolt.lifecycle")


class LifecycleHooks:
    """
    Manages startup and shutdown lifecycle hooks.

    Hooks are executed in registration order. Both sync and async handlers
    are supported - sync handlers are executed directly in the async context.
    """

    def __init__(self) -> None:
        self._startup_handlers: list[Callable[[], Any]] = []
        self._shutdown_handlers: list[Callable[[], Any]] = []
        self._startup_complete: bool = False
        self._shutdown_complete: bool = False

    def register_startup(self, handler: Callable[[], Any]) -> None:
        """
        Register a startup handler.

        Args:
            handler: A callable (sync or async) to run on startup.
                    Takes no arguments and return value is ignored.
        """
        self._startup_handlers.append(handler)

    def register_shutdown(self, handler: Callable[[], Any]) -> None:
        """
        Register a shutdown handler.

        Args:
            handler: A callable (sync or async) to run on shutdown.
                    Takes no arguments and return value is ignored.
        """
        self._shutdown_handlers.append(handler)

    async def run_startup(self) -> None:
        """
        Execute all startup handlers in registration order.

        Raises exceptions from handlers - failing to start is fatal.
        Sets _startup_complete to True after successful execution.
        """
        if self._startup_complete:
            logger.debug("Startup hooks already executed, skipping")
            return

        for handler in self._startup_handlers:
            handler_name = getattr(handler, "__name__", repr(handler))
            logger.debug(f"Running startup handler: {handler_name}")

            try:
                if inspect.iscoroutinefunction(handler):
                    await handler()
                else:
                    # Sync handler - call directly
                    handler()
            except Exception as e:
                logger.error(f"Startup handler '{handler_name}' failed: {e}")
                raise

        self._startup_complete = True
        logger.debug(f"Completed {len(self._startup_handlers)} startup handlers")

    async def run_shutdown(self) -> None:
        """
        Execute all shutdown handlers in registration order.

        Logs but does not raise exceptions - shutdown should complete
        even if individual handlers fail. Sets _shutdown_complete to True
        after execution (regardless of individual handler failures).
        """
        if self._shutdown_complete:
            logger.debug("Shutdown hooks already executed, skipping")
            return

        errors: list[tuple[str, Exception]] = []

        for handler in self._shutdown_handlers:
            handler_name = getattr(handler, "__name__", repr(handler))
            logger.debug(f"Running shutdown handler: {handler_name}")

            try:
                if inspect.iscoroutinefunction(handler):
                    await handler()
                else:
                    # Sync handler - call directly
                    handler()
            except Exception as e:
                logger.error(f"Shutdown handler '{handler_name}' failed: {e}")
                errors.append((handler_name, e))

        self._shutdown_complete = True
        logger.debug(f"Completed {len(self._shutdown_handlers)} shutdown handlers ({len(errors)} failed)")

    def run_startup_sync(self) -> None:
        """
        Run startup handlers synchronously.

        Creates a new event loop if needed. Used when called from
        synchronous context (e.g., management command before async server).
        """
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop is not None:
            # Already in async context - create task
            loop.run_until_complete(self.run_startup())
        else:
            # No event loop - run in new one
            asyncio.run(self.run_startup())

    def run_shutdown_sync(self) -> None:
        """
        Run shutdown handlers synchronously.

        Creates a new event loop if needed. Used when called from
        synchronous context (e.g., signal handler, atexit).
        """
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop is not None:
            # Already in async context - create task
            loop.run_until_complete(self.run_shutdown())
        else:
            # No event loop - run in new one
            asyncio.run(self.run_shutdown())

    @property
    def has_startup_handlers(self) -> bool:
        """Check if any startup handlers are registered."""
        return len(self._startup_handlers) > 0

    @property
    def has_shutdown_handlers(self) -> bool:
        """Check if any shutdown handlers are registered."""
        return len(self._shutdown_handlers) > 0

    def __repr__(self) -> str:
        return (
            f"LifecycleHooks("
            f"startup={len(self._startup_handlers)}, "
            f"shutdown={len(self._shutdown_handlers)}, "
            f"started={self._startup_complete}, "
            f"stopped={self._shutdown_complete})"
        )
