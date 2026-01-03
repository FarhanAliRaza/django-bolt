import asyncio

from django.utils.functional import LazyObject, empty


class AsyncLazyObject(LazyObject):
    """
    Async version of SimpleLazyObject that works in async context.
    """

    def __init__(self, async_func):
        self.__dict__["_setupfunc"] = async_func
        super().__init__()

    def _setup(self):
        if self._wrapped is empty:
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    self._wrapped = AsyncProxy(self._setupfunc)
                    return
            except RuntimeError:
                pass

            self._wrapped = asyncio.run(self._setupfunc())

    async def _async_setup(self):
        if self._wrapped is empty or isinstance(self._wrapped, AsyncProxy):
            self._wrapped = await self._setupfunc()

    def __getattr__(self, name):
        if self._wrapped is empty:
            self._setup()

        if isinstance(self._wrapped, AsyncProxy):
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    return AsyncAttribute(self, name)
            except RuntimeError:
                pass

        return getattr(self._wrapped, name)

    async def __aenter__(self):
        await self._async_setup()
        return self._wrapped

    async def __aexit__(self, *args):
        pass

    def __await__(self):
        async def wrapper():
            await self._async_setup()
            return self._wrapped

        return wrapper().__await__()


class AsyncProxy:
    def __init__(self, async_func):
        self._async_func = async_func

    async def __call__(self):
        return await self._async_func()


class AsyncAttribute:
    def __init__(self, lazy_obj, name):
        self._lazy_obj = lazy_obj
        self._name = name

    def __await__(self):
        async def wrapper():
            await self._lazy_obj._async_setup()
            return getattr(self._lazy_obj._wrapped, self._name)

        return wrapper().__await__()

    def __repr__(self):
        return f"<AsyncAttribute '{self._name}'>"
