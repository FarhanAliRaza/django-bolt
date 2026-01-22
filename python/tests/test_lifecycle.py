"""Tests for Django-Bolt lifecycle hooks (startup/shutdown)."""

import asyncio

import pytest

from django_bolt import BoltAPI, LifecycleHooks


class TestLifecycleHooks:
    """Test LifecycleHooks class."""

    def test_lifecycle_hooks_initialization(self):
        """Test LifecycleHooks initialization."""
        hooks = LifecycleHooks()
        assert hooks._startup_handlers == []
        assert hooks._shutdown_handlers == []
        assert hooks._startup_complete is False
        assert hooks._shutdown_complete is False

    def test_register_startup(self):
        """Test registering startup handlers."""
        hooks = LifecycleHooks()

        async def startup_handler():
            pass

        hooks.register_startup(startup_handler)
        assert len(hooks._startup_handlers) == 1
        assert hooks._startup_handlers[0] == startup_handler

    def test_register_shutdown(self):
        """Test registering shutdown handlers."""
        hooks = LifecycleHooks()

        async def shutdown_handler():
            pass

        hooks.register_shutdown(shutdown_handler)
        assert len(hooks._shutdown_handlers) == 1
        assert hooks._shutdown_handlers[0] == shutdown_handler

    def test_has_startup_handlers(self):
        """Test has_startup_handlers property."""
        hooks = LifecycleHooks()
        assert hooks.has_startup_handlers is False

        hooks.register_startup(lambda: None)
        assert hooks.has_startup_handlers is True

    def test_has_shutdown_handlers(self):
        """Test has_shutdown_handlers property."""
        hooks = LifecycleHooks()
        assert hooks.has_shutdown_handlers is False

        hooks.register_shutdown(lambda: None)
        assert hooks.has_shutdown_handlers is True

    @pytest.mark.asyncio
    async def test_run_startup_async_handler(self):
        """Test running async startup handlers."""
        hooks = LifecycleHooks()
        called = []

        async def async_startup():
            called.append("async_startup")

        hooks.register_startup(async_startup)
        await hooks.run_startup()

        assert called == ["async_startup"]
        assert hooks._startup_complete is True

    @pytest.mark.asyncio
    async def test_run_startup_sync_handler(self):
        """Test running sync startup handlers."""
        hooks = LifecycleHooks()
        called = []

        def sync_startup():
            called.append("sync_startup")

        hooks.register_startup(sync_startup)
        await hooks.run_startup()

        assert called == ["sync_startup"]
        assert hooks._startup_complete is True

    @pytest.mark.asyncio
    async def test_run_startup_mixed_handlers(self):
        """Test running mix of sync and async handlers."""
        hooks = LifecycleHooks()
        called = []

        def sync_startup():
            called.append("sync")

        async def async_startup():
            called.append("async")

        hooks.register_startup(sync_startup)
        hooks.register_startup(async_startup)
        await hooks.run_startup()

        assert called == ["sync", "async"]

    @pytest.mark.asyncio
    async def test_run_startup_order(self):
        """Test startup handlers run in registration order."""
        hooks = LifecycleHooks()
        order = []

        async def first():
            order.append(1)

        async def second():
            order.append(2)

        async def third():
            order.append(3)

        hooks.register_startup(first)
        hooks.register_startup(second)
        hooks.register_startup(third)
        await hooks.run_startup()

        assert order == [1, 2, 3]

    @pytest.mark.asyncio
    async def test_run_startup_only_once(self):
        """Test startup handlers only run once."""
        hooks = LifecycleHooks()
        count = [0]

        async def startup():
            count[0] += 1

        hooks.register_startup(startup)
        await hooks.run_startup()
        await hooks.run_startup()  # Second call should be no-op

        assert count[0] == 1
        assert hooks._startup_complete is True

    @pytest.mark.asyncio
    async def test_run_startup_exception_propagates(self):
        """Test startup handler exceptions propagate (fatal error)."""
        hooks = LifecycleHooks()

        async def failing_startup():
            raise RuntimeError("Startup failed!")

        hooks.register_startup(failing_startup)

        with pytest.raises(RuntimeError, match="Startup failed!"):
            await hooks.run_startup()

    @pytest.mark.asyncio
    async def test_run_shutdown_async_handler(self):
        """Test running async shutdown handlers."""
        hooks = LifecycleHooks()
        called = []

        async def async_shutdown():
            called.append("async_shutdown")

        hooks.register_shutdown(async_shutdown)
        await hooks.run_shutdown()

        assert called == ["async_shutdown"]
        assert hooks._shutdown_complete is True

    @pytest.mark.asyncio
    async def test_run_shutdown_sync_handler(self):
        """Test running sync shutdown handlers."""
        hooks = LifecycleHooks()
        called = []

        def sync_shutdown():
            called.append("sync_shutdown")

        hooks.register_shutdown(sync_shutdown)
        await hooks.run_shutdown()

        assert called == ["sync_shutdown"]

    @pytest.mark.asyncio
    async def test_run_shutdown_exception_logged_not_raised(self):
        """Test shutdown handler exceptions are logged but not raised."""
        hooks = LifecycleHooks()
        called = []

        async def failing_shutdown():
            called.append("failing")
            raise RuntimeError("Shutdown error!")

        async def second_shutdown():
            called.append("second")

        hooks.register_shutdown(failing_shutdown)
        hooks.register_shutdown(second_shutdown)

        # Should not raise, should continue to second handler
        await hooks.run_shutdown()

        assert "failing" in called
        assert "second" in called
        assert hooks._shutdown_complete is True

    @pytest.mark.asyncio
    async def test_run_shutdown_only_once(self):
        """Test shutdown handlers only run once."""
        hooks = LifecycleHooks()
        count = [0]

        async def shutdown():
            count[0] += 1

        hooks.register_shutdown(shutdown)
        await hooks.run_shutdown()
        await hooks.run_shutdown()  # Second call should be no-op

        assert count[0] == 1

    def test_run_startup_sync_method(self):
        """Test synchronous startup execution."""
        hooks = LifecycleHooks()
        called = []

        async def startup():
            called.append("startup")

        hooks.register_startup(startup)
        hooks.run_startup_sync()

        assert called == ["startup"]

    def test_run_shutdown_sync_method(self):
        """Test synchronous shutdown execution."""
        hooks = LifecycleHooks()
        called = []

        async def shutdown():
            called.append("shutdown")

        hooks.register_shutdown(shutdown)
        hooks.run_shutdown_sync()

        assert called == ["shutdown"]

    def test_repr(self):
        """Test LifecycleHooks repr."""
        hooks = LifecycleHooks()
        hooks.register_startup(lambda: None)
        hooks.register_shutdown(lambda: None)
        hooks.register_shutdown(lambda: None)

        repr_str = repr(hooks)
        assert "startup=1" in repr_str
        assert "shutdown=2" in repr_str
        assert "started=False" in repr_str
        assert "stopped=False" in repr_str


class TestBoltAPILifecycle:
    """Test BoltAPI lifecycle integration."""

    def test_api_has_lifecycle_hooks(self):
        """Test BoltAPI has lifecycle hooks attribute."""
        api = BoltAPI()
        assert hasattr(api, "_lifecycle")
        assert isinstance(api._lifecycle, LifecycleHooks)

    def test_on_startup_decorator(self):
        """Test @api.on_startup decorator."""
        api = BoltAPI()

        @api.on_startup
        async def startup():
            pass

        assert len(api._lifecycle._startup_handlers) == 1
        assert api._lifecycle._startup_handlers[0].__name__ == "startup"

    def test_on_startup_decorator_with_parens(self):
        """Test @api.on_startup() decorator with parentheses."""
        api = BoltAPI()

        @api.on_startup()
        async def startup():
            pass

        assert len(api._lifecycle._startup_handlers) == 1

    def test_on_shutdown_decorator(self):
        """Test @api.on_shutdown decorator."""
        api = BoltAPI()

        @api.on_shutdown
        async def shutdown():
            pass

        assert len(api._lifecycle._shutdown_handlers) == 1
        assert api._lifecycle._shutdown_handlers[0].__name__ == "shutdown"

    def test_on_shutdown_decorator_with_parens(self):
        """Test @api.on_shutdown() decorator with parentheses."""
        api = BoltAPI()

        @api.on_shutdown()
        async def shutdown():
            pass

        assert len(api._lifecycle._shutdown_handlers) == 1

    def test_on_startup_direct_registration(self):
        """Test api.on_startup(func) direct registration."""
        api = BoltAPI()

        async def startup():
            pass

        api.on_startup(startup)
        assert len(api._lifecycle._startup_handlers) == 1

    def test_on_shutdown_direct_registration(self):
        """Test api.on_shutdown(func) direct registration."""
        api = BoltAPI()

        async def shutdown():
            pass

        api.on_shutdown(shutdown)
        assert len(api._lifecycle._shutdown_handlers) == 1

    def test_multiple_startup_handlers(self):
        """Test registering multiple startup handlers."""
        api = BoltAPI()

        @api.on_startup
        async def startup1():
            pass

        @api.on_startup
        async def startup2():
            pass

        @api.on_startup
        async def startup3():
            pass

        assert len(api._lifecycle._startup_handlers) == 3

    def test_sync_startup_handler(self):
        """Test sync startup handler registration."""
        api = BoltAPI()

        @api.on_startup
        def sync_startup():
            pass

        assert len(api._lifecycle._startup_handlers) == 1

    def test_sync_shutdown_handler(self):
        """Test sync shutdown handler registration."""
        api = BoltAPI()

        @api.on_shutdown
        def sync_shutdown():
            pass

        assert len(api._lifecycle._shutdown_handlers) == 1

    @pytest.mark.asyncio
    async def test_api_lifecycle_execution(self):
        """Test BoltAPI lifecycle hooks execute correctly."""
        api = BoltAPI()
        state = {"started": False, "stopped": False}

        @api.on_startup
        async def startup():
            state["started"] = True

        @api.on_shutdown
        async def shutdown():
            state["stopped"] = True

        # Execute startup
        await api._lifecycle.run_startup()
        assert state["started"] is True
        assert state["stopped"] is False

        # Execute shutdown
        await api._lifecycle.run_shutdown()
        assert state["stopped"] is True

    @pytest.mark.asyncio
    async def test_startup_with_initialization(self):
        """Test realistic startup scenario with initialization."""
        api = BoltAPI()
        resources = {}

        @api.on_startup
        async def init_database():
            # Simulate database connection
            resources["db"] = "connected"

        @api.on_startup
        async def load_config():
            # Simulate loading configuration
            resources["config"] = {"debug": True}

        await api._lifecycle.run_startup()

        assert resources["db"] == "connected"
        assert resources["config"] == {"debug": True}

    @pytest.mark.asyncio
    async def test_shutdown_cleanup(self):
        """Test realistic shutdown scenario with cleanup."""
        api = BoltAPI()
        resources = {"db": "connected", "cache": "active"}

        @api.on_shutdown
        async def close_database():
            resources["db"] = "closed"

        @api.on_shutdown
        async def close_cache():
            resources["cache"] = "closed"

        await api._lifecycle.run_shutdown()

        assert resources["db"] == "closed"
        assert resources["cache"] == "closed"


class TestLifecycleEdgeCases:
    """Test edge cases and error scenarios."""

    @pytest.mark.asyncio
    async def test_empty_startup(self):
        """Test running startup with no handlers."""
        hooks = LifecycleHooks()
        await hooks.run_startup()  # Should not raise
        assert hooks._startup_complete is True

    @pytest.mark.asyncio
    async def test_empty_shutdown(self):
        """Test running shutdown with no handlers."""
        hooks = LifecycleHooks()
        await hooks.run_shutdown()  # Should not raise
        assert hooks._shutdown_complete is True

    @pytest.mark.asyncio
    async def test_startup_handler_with_await(self):
        """Test startup handler that awaits async operations."""
        hooks = LifecycleHooks()
        result = []

        async def startup_with_await():
            await asyncio.sleep(0.01)
            result.append("done")

        hooks.register_startup(startup_with_await)
        await hooks.run_startup()

        assert result == ["done"]

    def test_decorator_returns_original_function(self):
        """Test decorators return the original function unchanged."""
        api = BoltAPI()

        @api.on_startup
        async def my_startup():
            return "startup_result"

        # The function should be unchanged
        assert my_startup.__name__ == "my_startup"

    @pytest.mark.asyncio
    async def test_startup_exception_stops_execution(self):
        """Test that startup exception stops subsequent handlers."""
        hooks = LifecycleHooks()
        called = []

        async def first():
            called.append("first")
            raise RuntimeError("First failed")

        async def second():
            called.append("second")

        hooks.register_startup(first)
        hooks.register_startup(second)

        with pytest.raises(RuntimeError):
            await hooks.run_startup()

        # Second handler should not have been called
        assert called == ["first"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
