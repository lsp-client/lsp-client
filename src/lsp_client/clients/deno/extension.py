from __future__ import annotations

from collections.abc import Iterator, Sequence
from typing import Any, Protocol, override, runtime_checkable

from loguru import logger

from lsp_client.jsonrpc.id import jsonrpc_uuid
from lsp_client.protocol import (
    CapabilityClientProtocol,
    CapabilityProtocol,
    ExperimentalCapabilityProtocol,
    ServerNotificationHook,
    ServerRequestHookProtocol,
    ServerRequestHookRegistry,
)
from lsp_client.utils.types import AnyPath, lsp_type

from .models import (
    DENO_CACHE,
    DENO_PERFORMANCE,
    DENO_REGISTRY_STATE,
    DENO_RELOAD_IMPORT_REGISTRIES,
    DENO_TASK,
    DENO_TEST_MODULE,
    DENO_TEST_MODULE_DELETE,
    DENO_TEST_RUN,
    DENO_TEST_RUN_CANCEL,
    DENO_TEST_RUN_PROGRESS,
    DENO_VIRTUAL_TEXT_DOCUMENT,
    DenoCacheParams,
    DenoCacheRequest,
    DenoCacheResponse,
    DenoPerformanceRequest,
    DenoPerformanceResponse,
    DenoRegistryStatusNotification,
    DenoReloadImportRegistriesRequest,
    DenoReloadImportRegistriesResponse,
    DenoTaskRequest,
    DenoTaskResponse,
    DenoTestModuleDeleteNotification,
    DenoTestModuleNotification,
    DenoTestRunCancelParams,
    DenoTestRunCancelRequest,
    DenoTestRunCancelResponse,
    DenoTestRunProgressNotification,
    DenoTestRunRequest,
    DenoTestRunRequestParams,
    DenoTestRunResponse,
    DenoTestRunResponseParams,
    DenoVirtualTextDocumentParams,
    DenoVirtualTextDocumentRequest,
    DenoVirtualTextDocumentResponse,
)


@runtime_checkable
class WithRequestDenoCache(
    CapabilityProtocol,
    CapabilityClientProtocol,
    Protocol,
):
    """
    Capability protocol for Deno cache operations.

    Provides methods for caching dependencies in Deno's cache.

    Methods:
        request_deno_cache: Cache dependencies for a document

    Example:
        class DenoClient(WithRequestDenoCache, ...):
            ...
        client = DenoClient()
        await client.request_deno_cache("main.ts", ["import.ts"])
    """

    @override
    @classmethod
    def iter_methods(cls) -> Iterator[str]:
        yield from super().iter_methods()
        yield from (DENO_CACHE,)

    async def request_deno_cache(
        self,
        referrer: AnyPath,
        uris: Sequence[AnyPath] = (),
    ) -> None:
        return await self.request(
            DenoCacheRequest(
                id=jsonrpc_uuid(),
                params=DenoCacheParams(
                    referrer=lsp_type.TextDocumentIdentifier(uri=self.as_uri(referrer)),
                    uris=[
                        lsp_type.TextDocumentIdentifier(uri=self.as_uri(uri))
                        for uri in uris
                    ],
                ),
            ),
            schema=DenoCacheResponse,
        )


@runtime_checkable
class WithRequestDenoPerformance(
    CapabilityProtocol,
    CapabilityClientProtocol,
    Protocol,
):
    """
    Capability protocol for Deno performance metrics.

    Provides methods for querying Deno runtime performance information.

    Methods:
        request_deno_performance: Get performance metrics

    Example:
        class DenoClient(WithRequestDenoPerformance, ...):
            ...
        client = DenoClient()
        metrics = await client.request_deno_performance()
    """

    @override
    @classmethod
    def iter_methods(cls) -> Iterator[str]:
        yield from super().iter_methods()
        yield from (DENO_PERFORMANCE,)

    async def request_deno_performance(self) -> Any:  # noqa: ANN401
        return await self.request(
            DenoPerformanceRequest(id=jsonrpc_uuid()),
            schema=DenoPerformanceResponse,
        )


@runtime_checkable
class WithRequestDenoReloadImportRegistries(
    CapabilityProtocol,
    CapabilityClientProtocol,
    Protocol,
):
    """
    Capability protocol for Deno import registry reloading.

    Provides methods for refreshing Deno's import registry cache.

    Methods:
        request_deno_reload_import_registries: Reload import registry caches

    Example:
        class DenoClient(WithRequestDenoReloadImportRegistries, ...):
            ...
        client = DenoClient()
        await client.request_deno_reload_import_registries()
    """

    @override
    @classmethod
    def iter_methods(cls) -> Iterator[str]:
        yield from super().iter_methods()
        yield from (DENO_RELOAD_IMPORT_REGISTRIES,)

    async def request_deno_reload_import_registries(self) -> None:
        return await self.request(
            DenoReloadImportRegistriesRequest(id=jsonrpc_uuid()),
            schema=DenoReloadImportRegistriesResponse,
        )


@runtime_checkable
class WithRequestDenoVirtualTextDocument(
    CapabilityProtocol,
    CapabilityClientProtocol,
    Protocol,
):
    """
    Capability protocol for Deno virtual text documents.

    Provides methods for opening special virtual documents in Deno,
    such as inline JSDoc views or other generated content.

    Methods:
        request_deno_virtual_text_document: Open a virtual text document

    Example:
        class DenoClient(WithRequestDenoVirtualTextDocument, ...):
            ...
        client = DenoClient()
        content = await client.request_deno_virtual_text_document("deno:/asset:///...")
    """

    @override
    @classmethod
    def iter_methods(cls) -> Iterator[str]:
        yield from super().iter_methods()
        yield from (DENO_VIRTUAL_TEXT_DOCUMENT,)

    async def request_deno_virtual_text_document(
        self,
        uri: str,
    ) -> str:
        return await self.request(
            DenoVirtualTextDocumentRequest(
                id=jsonrpc_uuid(),
                params=DenoVirtualTextDocumentParams(
                    text_document=lsp_type.TextDocumentIdentifier(uri=uri)
                ),
            ),
            schema=DenoVirtualTextDocumentResponse,
        )


@runtime_checkable
class WithRequestDenoTask(
    CapabilityProtocol,
    CapabilityClientProtocol,
    Protocol,
):
    """
    Capability protocol for Deno task execution.

    Provides methods for running Deno tasks defined in deno.json.

    Methods:
        request_deno_task: Execute a Deno task

    Example:
        class DenoClient(WithRequestDenoTask, ...):
            ...
        client = DenoClient()
        results = await client.request_deno_task()
    """

    @override
    @classmethod
    def iter_methods(cls) -> Iterator[str]:
        yield from super().iter_methods()
        yield from (DENO_TASK,)

    async def request_deno_task(self) -> list[Any]:
        return await self.request(
            DenoTaskRequest(id=jsonrpc_uuid()),
            schema=DenoTaskResponse,
        )


@runtime_checkable
class WithRequestDenoTestRun(
    ExperimentalCapabilityProtocol,
    CapabilityProtocol,
    CapabilityClientProtocol,
    Protocol,
):
    """
    Capability protocol for Deno test execution.

    Provides methods for running Deno tests. This is an experimental capability
    that requires the testingApi feature flag.

    Methods:
        request_deno_test_run: Start a test run

    Example:
        class DenoClient(WithRequestDenoTestRun, ...):
            ...
        client = DenoClient()
        params = DenoTestRunRequestParams(id=1, kind="run")
        result = await client.request_deno_test_run(params)
    """

    @override
    @classmethod
    def iter_methods(cls) -> Iterator[str]:
        yield from super().iter_methods()
        yield from (DENO_TEST_RUN,)

    @override
    @classmethod
    def register_experimental_capability(cls, cap: dict[str, Any]) -> None:
        cap["testingApi"] = True

    async def request_deno_test_run(
        self,
        params: DenoTestRunRequestParams,
    ) -> DenoTestRunResponseParams:
        return await self.request(
            DenoTestRunRequest(
                id=jsonrpc_uuid(),
                params=params,
            ),
            schema=DenoTestRunResponse,
        )


@runtime_checkable
class WithRequestDenoTestRunCancel(
    CapabilityProtocol,
    CapabilityClientProtocol,
    Protocol,
):
    """
    Capability protocol for cancelling Deno test runs.

    Provides methods for cancelling running Deno tests.

    Methods:
        request_deno_test_run_cancel: Cancel a running test

    Example:
        class DenoClient(WithRequestDenoTestRunCancel, ...):
            ...
        client = DenoClient()
        await client.request_deno_test_run_cancel(test_run_id=1)
    """

    @override
    @classmethod
    def iter_methods(cls) -> Iterator[str]:
        yield from super().iter_methods()
        yield from (DENO_TEST_RUN_CANCEL,)

    async def request_deno_test_run_cancel(
        self,
        test_run_id: int,
    ) -> None:
        return await self.request(
            DenoTestRunCancelRequest(
                id=jsonrpc_uuid(),
                params=DenoTestRunCancelParams(id=test_run_id),
            ),
            schema=DenoTestRunCancelResponse,
        )


@runtime_checkable
class WithReceiveDenoRegistryStatus(
    ServerRequestHookProtocol,
    CapabilityClientProtocol,
    Protocol,
):
    """
    Capability protocol for receiving Deno registry status notifications.

    Provides handlers for import registry state changes from Deno.

    Methods:
        receive_deno_registry_state: Handle registry status notifications

    Example:
        class DenoClient(WithReceiveDenoRegistryStatus, ...):
            async def receive_deno_registry_state(self, noti):
                print(f"Registry suggestions: {noti.params.suggestions}")
    """

    @override
    @classmethod
    def iter_methods(cls) -> Iterator[str]:
        yield from super().iter_methods()
        yield from (DENO_REGISTRY_STATE,)

    async def receive_deno_registry_state(
        self, noti: DenoRegistryStatusNotification
    ) -> None:
        logger.debug("Received Deno registry state: {}", noti.params)

    @override
    def register_server_request_hooks(
        self, registry: ServerRequestHookRegistry
    ) -> None:
        super().register_server_request_hooks(registry)
        registry.register(
            DENO_REGISTRY_STATE,
            ServerNotificationHook(
                cls=DenoRegistryStatusNotification,
                execute=self.receive_deno_registry_state,
            ),
        )


@runtime_checkable
class WithReceiveDenoTestModule(
    ServerRequestHookProtocol,
    CapabilityClientProtocol,
    Protocol,
):
    """
    Capability protocol for receiving Deno test module notifications.

    Provides handlers for test discovery notifications from Deno.

    Methods:
        receive_deno_test_module: Handle test module discovery

    Example:
        class DenoClient(WithReceiveDenoTestModule, ...):
            async def receive_deno_test_module(self, noti):
                for test in noti.params.tests:
                    print(f"Found test: {test.label}")
    """

    @override
    @classmethod
    def iter_methods(cls) -> Iterator[str]:
        yield from super().iter_methods()
        yield from (DENO_TEST_MODULE,)

    async def receive_deno_test_module(self, noti: DenoTestModuleNotification) -> None:
        logger.debug("Received Deno test module: {}", noti.params)

    @override
    def register_server_request_hooks(
        self, registry: ServerRequestHookRegistry
    ) -> None:
        super().register_server_request_hooks(registry)
        registry.register(
            DENO_TEST_MODULE,
            ServerNotificationHook(
                cls=DenoTestModuleNotification,
                execute=self.receive_deno_test_module,
            ),
        )


@runtime_checkable
class WithReceiveDenoTestModuleDelete(
    ServerRequestHookProtocol,
    CapabilityClientProtocol,
    Protocol,
):
    """
    Capability protocol for receiving Deno test module deletion notifications.

    Provides handlers for test removal notifications from Deno.

    Methods:
        receive_deno_test_module_delete: Handle test module removal

    Example:
        class DenoClient(WithReceiveDenoTestModuleDelete, ...):
            async def receive_deno_test_module_delete(self, noti):
                print(f"Tests removed from: {noti.params.text_document.uri}")
    """

    @override
    @classmethod
    def iter_methods(cls) -> Iterator[str]:
        yield from super().iter_methods()
        yield from (DENO_TEST_MODULE_DELETE,)

    async def receive_deno_test_module_delete(
        self, noti: DenoTestModuleDeleteNotification
    ) -> None:
        logger.debug("Received Deno test module delete: {}", noti.params)

    @override
    def register_server_request_hooks(
        self, registry: ServerRequestHookRegistry
    ) -> None:
        super().register_server_request_hooks(registry)
        registry.register(
            DENO_TEST_MODULE_DELETE,
            ServerNotificationHook(
                cls=DenoTestModuleDeleteNotification,
                execute=self.receive_deno_test_module_delete,
            ),
        )


@runtime_checkable
class WithReceiveDenoTestRunProgress(
    ServerRequestHookProtocol,
    CapabilityClientProtocol,
    Protocol,
):
    """
    Capability protocol for receiving Deno test run progress notifications.

    Provides handlers for test execution progress updates from Deno.

    Methods:
        receive_deno_test_run_progress: Handle test progress updates

    Example:
        class DenoClient(WithReceiveDenoTestRunProgress, ...):
            async def receive_deno_test_run_progress(self, noti):
                msg = noti.params.message
                print(f"Test run {noti.params.id}: {msg.type}")
    """

    @override
    @classmethod
    def iter_methods(cls) -> Iterator[str]:
        yield from super().iter_methods()
        yield from (DENO_TEST_RUN_PROGRESS,)

    async def receive_deno_test_run_progress(
        self, noti: DenoTestRunProgressNotification
    ) -> None:
        logger.debug("Received Deno test run progress: {}", noti.params)

    @override
    def register_server_request_hooks(
        self, registry: ServerRequestHookRegistry
    ) -> None:
        super().register_server_request_hooks(registry)
        registry.register(
            DENO_TEST_RUN_PROGRESS,
            ServerNotificationHook(
                cls=DenoTestRunProgressNotification,
                execute=self.receive_deno_test_run_progress,
            ),
        )
