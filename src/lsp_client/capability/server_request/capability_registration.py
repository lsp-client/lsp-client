from __future__ import annotations

from collections.abc import Iterator
from typing import Protocol, override, runtime_checkable

from loguru import logger

from lsp_client.protocol import (
    CapabilityClientProtocol,
    ServerRequestHook,
    ServerRequestHookProtocol,
    ServerRequestHookRegistry,
)
from lsp_client.utils.types import lsp_type


@runtime_checkable
class WithRespondCapabilityRegistration(
    ServerRequestHookProtocol,
    CapabilityClientProtocol,
    Protocol,
):
    """
    `client/registerCapability` and `client/unregisterCapability`
    - https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#client_registerCapability
    - https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#client_unregisterCapability
    """

    @override
    @classmethod
    def iter_methods(cls) -> Iterator[str]:
        yield from super().iter_methods()
        yield lsp_type.CLIENT_REGISTER_CAPABILITY
        yield lsp_type.CLIENT_UNREGISTER_CAPABILITY

    async def respond_register_capability(
        self, req: lsp_type.RegistrationRequest
    ) -> lsp_type.RegistrationResponse:
        logger.debug("Received client/registerCapability request")
        # Behavior not implemented as requested
        return lsp_type.RegistrationResponse(id=req.id, result=None)

    async def respond_unregister_capability(
        self, req: lsp_type.UnregistrationRequest
    ) -> lsp_type.UnregistrationResponse:
        logger.debug("Received client/unregisterCapability request")
        # Behavior not implemented as requested
        return lsp_type.UnregistrationResponse(id=req.id, result=None)

    @override
    def register_server_request_hooks(
        self, registry: ServerRequestHookRegistry
    ) -> None:
        super().register_server_request_hooks(registry)

        registry.register(
            lsp_type.CLIENT_REGISTER_CAPABILITY,
            ServerRequestHook(
                cls=lsp_type.RegistrationRequest,
                execute=self.respond_register_capability,
            ),
        )
        registry.register(
            lsp_type.CLIENT_UNREGISTER_CAPABILITY,
            ServerRequestHook(
                cls=lsp_type.UnregistrationRequest,
                execute=self.respond_unregister_capability,
            ),
        )
