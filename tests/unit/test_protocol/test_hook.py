from __future__ import annotations

from typing import Any
from unittest.mock import patch

from attrs import define
from loguru import logger

from lsp_client.protocol.hook import (
    ServerNotificationHook,
    ServerRequestHook,
    ServerRequestHookRegistry,
)


@define
class MockRequest:
    method: str = "test/request"


@define
class MockNotification:
    method: str = "test/notification"


@define
class MockResponse:
    result: Any = None


async def mock_request_handler(req: MockRequest) -> MockResponse:
    return MockResponse()


async def mock_notification_handler(noti: MockNotification) -> None:
    pass


def test_server_request_hook_registry():
    registry = ServerRequestHookRegistry()

    # Test request hook registration
    req_hook: ServerRequestHook[MockRequest] = ServerRequestHook(
        cls=MockRequest, execute=mock_request_handler
    )
    registry.register("test/request", req_hook)
    assert registry.get_request_hook("test/request") == req_hook

    # Test notification hook registration
    noti_hook: ServerNotificationHook[MockNotification] = ServerNotificationHook(
        cls=MockNotification, execute=mock_notification_handler
    )
    registry.register("test/notification", noti_hook)
    assert noti_hook in registry.get_notification_hooks("test/notification")
    assert len(registry.get_notification_hooks("test/notification")) == 1

    # Test multiple notification hooks
    async def another_handler(noti: MockNotification) -> None:
        pass

    noti_hook2: ServerNotificationHook[MockNotification] = ServerNotificationHook(
        cls=MockNotification, execute=another_handler
    )
    registry.register("test/notification", noti_hook2)
    assert len(registry.get_notification_hooks("test/notification")) == 2
    assert noti_hook in registry.get_notification_hooks("test/notification")
    assert noti_hook2 in registry.get_notification_hooks("test/notification")


def test_server_request_hook_registry_overwrite_warning():
    registry = ServerRequestHookRegistry()

    req_hook1: ServerRequestHook[MockRequest] = ServerRequestHook(
        cls=MockRequest, execute=mock_request_handler
    )
    registry.register("test/request", req_hook1)

    req_hook2: ServerRequestHook[MockRequest] = ServerRequestHook(
        cls=MockRequest, execute=mock_request_handler
    )
    with patch.object(logger, "warning") as mock_warning:
        registry.register("test/request", req_hook2)

    assert registry.get_request_hook("test/request") == req_hook2
    mock_warning.assert_called_once_with(
        "Overwriting existing request hook for method `{}`", "test/request"
    )
