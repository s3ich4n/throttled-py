from collections.abc import Awaitable, Callable

import pytest
from throttled import Hook, Throttled, per_sec
from throttled.asyncio import AsyncHook
from throttled.asyncio import Throttled as AsyncThrottled
from throttled.rate_limiter import RateLimitResult


class SyncNoopHook(Hook):
    def on_limit(  # noqa: PLR6301
        self,
        call_next: Callable[[], RateLimitResult],
        context,  # noqa: ANN001
    ) -> RateLimitResult:
        return call_next()


class AsyncNoopHook(AsyncHook):
    async def on_limit(  # noqa: PLR6301
        self,
        call_next: Callable[[], Awaitable[RateLimitResult]],
        context,  # noqa: ANN001
    ) -> RateLimitResult:
        return await call_next()


class NotAHook:
    pass


class TestHookTypeValidation:
    @classmethod
    def test_sync_throttled_rejects_non_hook(cls) -> None:
        with pytest.raises(TypeError):
            Throttled(key="k", quota=per_sec(1), hooks=[NotAHook()])

    @classmethod
    def test_sync_throttled_rejects_async_hook(cls) -> None:
        with pytest.raises(TypeError):
            Throttled(key="k", quota=per_sec(1), hooks=[AsyncNoopHook()])

    @classmethod
    def test_async_throttled_rejects_non_hook(cls) -> None:
        with pytest.raises(TypeError):
            AsyncThrottled(key="k", quota=per_sec(1), hooks=[NotAHook()])

    @classmethod
    def test_async_throttled_rejects_sync_hook(cls) -> None:
        with pytest.raises(TypeError):
            AsyncThrottled(key="k", quota=per_sec(1), hooks=[SyncNoopHook()])


class TestHookContainerBehavior:
    @classmethod
    def test_sync_throttled_stores_hooks_as_tuple_when_given_list(cls) -> None:
        hooks = [SyncNoopHook(), SyncNoopHook()]
        throttle = Throttled(key="k", quota=per_sec(1), hooks=hooks)

        assert isinstance(throttle._hooks, tuple)
        assert throttle._hooks == tuple(hooks)

    @classmethod
    def test_sync_throttled_stores_hooks_as_tuple_when_given_tuple(cls) -> None:
        hooks = (SyncNoopHook(), SyncNoopHook())
        throttle = Throttled(key="k", quota=per_sec(1), hooks=hooks)

        assert isinstance(throttle._hooks, tuple)
        assert throttle._hooks == hooks

    @classmethod
    def test_async_throttled_stores_hooks_as_tuple_when_given_tuple(cls) -> None:
        hooks = (AsyncNoopHook(), AsyncNoopHook())
        throttle = AsyncThrottled(key="k", quota=per_sec(1), hooks=hooks)

        assert isinstance(throttle._hooks, tuple)
        assert throttle._hooks == hooks
