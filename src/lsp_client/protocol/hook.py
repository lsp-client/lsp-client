"""Server request and notification hook system for LSP client.

Defines hooks for handling server-initiated requests and notifications,
with a registry for managing and dispatching these hooks.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from attr import define
from attrs import Factory, frozen
from loguru import logger

from lsp_client.utils.types import Notification, Request, Response

from .capability import CapabilityProtocol


class ServerRequestHookExecutor[R: Request](Protocol):
    """
    Protocol for executing server-initiated request hooks.

    Defines the callable signature for handling requests sent by the
    language server to the client.

    Type Parameters:
        R: The request type this executor handles

    Example:
        async def handle_complete(req: CompletionRequest) -> CompletionList:
            ...
    """

    async def __call__(self, /, req: R) -> Response: ...


@frozen
class ServerRequestHook[R: Request]:
    """
    Registry entry for a server-initiated request hook.

    Associates a request type with its executor function for handling
    requests sent by the language server.

    Type Parameters:
        R: The request type this hook handles

    Attributes:
        cls: The request class/type
        execute: Async callable that processes the request

    Example:
        hook = ServerRequestHook(
            cls=CompletionRequest,
            execute=handle_completion
        )
    """

    cls: type[R]
    execute: ServerRequestHookExecutor[R]


class ServerNotificationHookExecutor[N: Notification](Protocol):
    """
    Protocol for executing server-initiated notification hooks.

    Defines the callable signature for handling notifications sent by the
    language server to the client.

    Type Parameters:
        N: The notification type this executor handles

    Example:
        async def handle_log_message(msg: LogMessageNotification) -> None:
            ...
    """

    async def __call__(self, /, noti: N) -> None: ...


@frozen
class ServerNotificationHook[N: Notification]:
    """
    Registry entry for a server-initiated notification hook.

    Associates a notification type with its executor function for handling
    notifications sent by the language server.

    Type Parameters:
        N: The notification type this hook handles

    Attributes:
        cls: The notification class/type
        execute: Async callable that processes the notification

    Example:
        hook = ServerNotificationHook(
            cls=LogMessageNotification,
            execute=handle_log_message
        )
    """

    cls: type[N]
    execute: ServerNotificationHookExecutor[N]


@define
class ServerRequestHookRegistry:
    """
    Registry for managing server-initiated request and notification hooks.

    Maintains mappings of LSP method names to their corresponding hook
    handlers. Supports both request hooks (single handler per method)
    and notification hooks (multiple handlers per method).

    Attributes:
        _req: Maps request method names to their hooks
        _noti: Maps notification method names to sets of hooks

    Example:
        registry = ServerRequestHookRegistry()
        registry.register("textDocument/publishDiagnostics", diagnostic_hook)
        if hook := registry.get_request_hook("textDocument/publishDiagnostics"):
            await hook.execute(request)
    """

    _req: dict[str, ServerRequestHook] = Factory(dict)
    _noti: dict[str, set[ServerNotificationHook]] = Factory(dict)

    def register(
        self,
        method: str,
        hook: ServerRequestHook | ServerNotificationHook,
    ) -> None:
        match hook:
            case ServerRequestHook():
                if method in self._req:
                    logger.warning(
                        "Overwriting existing request hook for method `{}`", method
                    )
                self._req[method] = hook
            case ServerNotificationHook():
                self._noti.setdefault(method, set()).add(hook)

    def get_request_hook(self, method: str) -> ServerRequestHook | None:
        return self._req.get(method)

    def get_notification_hooks(self, method: str) -> set[ServerNotificationHook]:
        return self._noti.get(method, set())


@runtime_checkable
class ServerRequestHookProtocol(CapabilityProtocol, Protocol):
    def register_server_request_hooks(
        self, registry: ServerRequestHookRegistry
    ) -> None:
        """Register request hooks to the registry."""
