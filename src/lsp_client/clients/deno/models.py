from __future__ import annotations

from typing import Any, Literal

import cattrs
from attrs import define, field, resolve_types
from lsprotocol import converters

from lsp_client.jsonrpc.id import ID
from lsp_client.utils.types import lsp_type

# ---------------------------------- Constants --------------------------------- #

DENO_CACHE: Literal["deno/cache"] = "deno/cache"
DENO_PERFORMANCE: Literal["deno/performance"] = "deno/performance"
DENO_RELOAD_IMPORT_REGISTRIES: Literal["deno/reloadImportRegistries"] = (
    "deno/reloadImportRegistries"
)
DENO_VIRTUAL_TEXT_DOCUMENT: Literal["deno/virtualTextDocument"] = (
    "deno/virtualTextDocument"
)
DENO_TASK: Literal["deno/task"] = "deno/task"
DENO_REGISTRY_STATE: Literal["deno/registryState"] = "deno/registryState"
DENO_TEST_RUN: Literal["deno/testRun"] = "deno/testRun"
DENO_TEST_RUN_CANCEL: Literal["deno/testRunCancel"] = "deno/testRunCancel"
DENO_TEST_MODULE: Literal["deno/testModule"] = "deno/testModule"
DENO_TEST_MODULE_DELETE: Literal["deno/testModuleDelete"] = "deno/testModuleDelete"
DENO_TEST_RUN_PROGRESS: Literal["deno/testRunProgress"] = "deno/testRunProgress"


# --------------------------------- Base Types -------------------------------- #


@define
class DenoTestData:
    """
    Represents a Deno test case or test suite.

    Attributes:
        id: Unique identifier for the test
        label: Human-readable test name
        steps: Nested sub-tests for test suites
        range: Source code range of the test definition
    """

    id: str
    label: str
    steps: list[DenoTestData] | None = None
    range: lsp_type.Range | None = None


@define
class DenoTestIdentifier:
    """
    Identifies a specific test or test step in Deno.

    Attributes:
        text_document: The document containing the test
        id: Test identifier (None if using step_id)
        step_id: Step identifier within a test (None if using id)
    """

    text_document: lsp_type.TextDocumentIdentifier
    id: str | None = None
    step_id: str | None = None


@define
class DenoTestMessage:
    """
    Represents a test result message in Deno test runner.

    Attributes:
        message: The test message content (formatted)
        expected_output: Expected output for assertion failures
        actual_output: Actual output for assertion failures
        location: Source location of the test message
    """

    message: lsp_type.MarkupContent
    expected_output: str | None = None
    actual_output: str | None = None
    location: lsp_type.Location | None = None


@define
class DenoTestEnqueuedStartedSkipped:
    """
    Represents a test that was enqueued, started, or skipped.

    Attributes:
        type: Event type ("enqueued", "started", or "skipped")
        test: The test identifier
    """

    type: Literal["enqueued", "started", "skipped"]
    test: DenoTestIdentifier


@define
class DenoTestFailedErrored:
    """
    Represents a test that failed or errored.

    Attributes:
        type: Event type ("failed" or "errored")
        test: The test identifier
        messages: List of test result messages
        duration: Test execution time in milliseconds
    """

    type: Literal["failed", "errored"]
    test: DenoTestIdentifier
    messages: list[DenoTestMessage]
    duration: float | None = None


@define
class DenoTestPassed:
    """
    Represents a test that passed.

    Attributes:
        type: Event type ("passed")
        test: The test identifier
        duration: Test execution time in milliseconds
    """

    type: Literal["passed"]
    test: DenoTestIdentifier
    duration: float | None = None


@define
class DenoTestOutput:
    """
    Represents console output during test execution.

    Attributes:
        type: Event type ("output")
        value: The output string
        test: Associated test identifier if output is test-related
        location: Source location of the output
    """

    type: Literal["output"]
    value: str
    test: DenoTestIdentifier | None = None
    location: lsp_type.Location | None = None


@define
class DenoTestEnd:
    """
    Represents the end of a test run.

    Attributes:
        type: Event type ("end")
    """

    type: Literal["end"]


type DenoTestRunProgressMessage = (
    DenoTestEnqueuedStartedSkipped
    | DenoTestFailedErrored
    | DenoTestPassed
    | DenoTestOutput
    | DenoTestEnd
)


@define
class DenoEnqueuedTestModule:
    """
    Represents a test module that was enqueued for execution.

    Attributes:
        text_document: The document containing the test module
        ids: List of test IDs in this module
    """

    text_document: lsp_type.TextDocumentIdentifier
    ids: list[str]


# ---------------------------------- Requests --------------------------------- #


@define
class DenoCacheParams:
    """
    Parameters for the deno/cache request.

    Attributes:
        referrer: Document to cache dependencies for
        uris: Additional documents to cache
    """

    referrer: lsp_type.TextDocumentIdentifier
    uris: list[lsp_type.TextDocumentIdentifier] = field(factory=list)


@define
class DenoCacheRequest:
    """
    Request to cache dependencies in Deno's cache.

    Method: deno/cache

    Attributes:
        id: JSON-RPC request ID
        params: Cache parameters
        method: Fixed value "deno/cache"
        jsonrpc: JSON-RPC version (always "2.0")
    """

    id: ID
    params: DenoCacheParams
    method: Literal["deno/cache"] = DENO_CACHE
    jsonrpc: str = "2.0"


@define
class DenoCacheResponse:
    """
    Response to the deno/cache request.

    Attributes:
        id: JSON-RPC response ID (None for notifications)
        result: Always None for this response
        jsonrpc: JSON-RPC version (always "2.0")
    """

    id: ID | None
    result: None
    jsonrpc: str = "2.0"


@define
class DenoPerformanceRequest:
    """
    Request for Deno performance metrics.

    Method: deno/performance

    Attributes:
        id: JSON-RPC request ID
        method: Fixed value "deno/performance"
        jsonrpc: JSON-RPC version (always "2.0")
    """

    id: ID
    method: Literal["deno/performance"] = DENO_PERFORMANCE
    jsonrpc: str = "2.0"


@define
class DenoPerformanceResponse:
    """
    Response containing Deno performance metrics.

    Attributes:
        id: JSON-RPC response ID (None for notifications)
        result: Performance metrics data
        jsonrpc: JSON-RPC version (always "2.0")
    """

    id: ID | None
    result: Any
    jsonrpc: str = "2.0"


@define
class DenoReloadImportRegistriesRequest:
    """
    Request to reload Deno import registry caches.

    Method: deno/reloadImportRegistries

    Attributes:
        id: JSON-RPC request ID
        method: Fixed value "deno/reloadImportRegistries"
        jsonrpc: JSON-RPC version (always "2.0")
    """

    id: ID
    method: Literal["deno/reloadImportRegistries"] = DENO_RELOAD_IMPORT_REGISTRIES
    jsonrpc: str = "2.0"


@define
class DenoReloadImportRegistriesResponse:
    """
    Response to the deno/reloadImportRegistries request.

    Attributes:
        id: JSON-RPC response ID (None for notifications)
        result: Always None for this response
        jsonrpc: JSON-RPC version (always "2.0")
    """

    id: ID | None
    result: None
    jsonrpc: str = "2.0"


@define
class DenoVirtualTextDocumentParams:
    """
    Parameters for the deno/virtualTextDocument request.

    Attributes:
        text_document: The document to open as virtual text
    """

    text_document: lsp_type.TextDocumentIdentifier


@define
class DenoVirtualTextDocumentRequest:
    """
    Request to open a virtual text document in Deno.

    Method: deno/virtualTextDocument

    Attributes:
        id: JSON-RPC request ID
        params: Virtual document parameters
        method: Fixed value "deno/virtualTextDocument"
        jsonrpc: JSON-RPC version (always "2.0")
    """

    id: ID
    params: DenoVirtualTextDocumentParams
    method: Literal["deno/virtualTextDocument"] = DENO_VIRTUAL_TEXT_DOCUMENT
    jsonrpc: str = "2.0"


@define
class DenoVirtualTextDocumentResponse:
    """
    Response containing virtual document content.

    Attributes:
        id: JSON-RPC response ID (None for notifications)
        result: The text content of the virtual document
        jsonrpc: JSON-RPC version (always "2.0")
    """

    id: ID | None
    result: str
    jsonrpc: str = "2.0"


@define
class DenoTaskParams:
    """
    Parameters for the deno/task request.

    Currently an empty placeholder for future task configuration.
    """


@define
class DenoTaskRequest:
    """
    Request to execute Deno tasks.

    Method: deno/task

    Attributes:
        id: JSON-RPC request ID
        params: Task parameters (currently unused)
        method: Fixed value "deno/task"
        jsonrpc: JSON-RPC version (always "2.0")
    """

    id: ID
    params: DenoTaskParams | None = None
    method: Literal["deno/task"] = DENO_TASK
    jsonrpc: str = "2.0"


@define
class DenoTaskResponse:
    """
    Response containing Deno task execution results.

    Attributes:
        id: JSON-RPC response ID (None for notifications)
        result: List of task results
        jsonrpc: JSON-RPC version (always "2.0")
    """

    id: ID | None
    result: list[Any]
    jsonrpc: str = "2.0"


@define
class DenoTestRunRequestParams:
    """
    Parameters for the deno/testRun request.

    Attributes:
        id: Unique identifier for this test run
        kind: Type of test run ("run", "coverage", or "debug")
        exclude: Tests to exclude from the run
        include: Tests to include in the run
    """

    id: int
    kind: Literal["run", "coverage", "debug"]
    exclude: list[DenoTestIdentifier] | None = None
    include: list[DenoTestIdentifier] | None = None


@define
class DenoTestRunRequest:
    """
    Request to start a Deno test run.

    Method: deno/testRun

    Attributes:
        id: JSON-RPC request ID
        params: Test run parameters
        method: Fixed value "deno/testRun"
        jsonrpc: JSON-RPC version (always "2.0")
    """

    id: ID
    params: DenoTestRunRequestParams
    method: Literal["deno/testRun"] = DENO_TEST_RUN
    jsonrpc: str = "2.0"


@define
class DenoTestRunResponseParams:
    """
    Response parameters for a test run request.

    Attributes:
        enqueued: List of test modules that were enqueued
    """

    enqueued: list[DenoEnqueuedTestModule]


@define
class DenoTestRunResponse:
    """
    Response to the deno/testRun request.

    Attributes:
        id: JSON-RPC response ID (None for notifications)
        result: Test run response parameters
        jsonrpc: JSON-RPC version (always "2.0")
    """

    id: ID | None
    result: DenoTestRunResponseParams
    jsonrpc: str = "2.0"


@define
class DenoTestRunCancelParams:
    """
    Parameters for the deno/testRunCancel request.

    Attributes:
        id: The test run ID to cancel
    """

    id: int


@define
class DenoTestRunCancelRequest:
    """
    Request to cancel a running Deno test.

    Method: deno/testRunCancel

    Attributes:
        id: JSON-RPC request ID
        params: Cancel parameters
        method: Fixed value "deno/testRunCancel"
        jsonrpc: JSON-RPC version (always "2.0")
    """

    id: ID
    params: DenoTestRunCancelParams
    method: Literal["deno/testRunCancel"] = DENO_TEST_RUN_CANCEL
    jsonrpc: str = "2.0"


@define
class DenoTestRunCancelResponse:
    """
    Response to the deno/testRunCancel request.

    Attributes:
        id: JSON-RPC response ID (None for notifications)
        result: Always None for this response
        jsonrpc: JSON-RPC version (always "2.0")
    """

    id: ID | None
    result: None
    jsonrpc: str = "2.0"


# -------------------------------- Notifications ------------------------------- #


@define
class DenoRegistryStatusNotificationParams:
    """
    Parameters for the deno/registryState notification.

    Attributes:
        origin: The import origin that triggered the notification
        suggestions: Whether import suggestions are available
    """

    origin: str
    suggestions: bool


@define
class DenoRegistryStatusNotification:
    """
    Notification about import registry status from Deno.

    Method: deno/registryState

    Attributes:
        params: Registry status parameters
        method: Fixed value "deno/registryState"
        jsonrpc: JSON-RPC version (always "2.0")
    """

    params: DenoRegistryStatusNotificationParams
    method: Literal["deno/registryState"] = DENO_REGISTRY_STATE
    jsonrpc: str = "2.0"


@define
class DenoTestModuleParams:
    """
    Parameters for the deno/testModule notification.

    Attributes:
        text_document: The document containing the tests
        kind: Type of change ("insert" or "replace")
        label: Name of the test module
        tests: List of tests in this module
    """

    text_document: lsp_type.TextDocumentIdentifier
    kind: Literal["insert", "replace"]
    label: str
    tests: list[DenoTestData]


@define
class DenoTestModuleNotification:
    """
    Notification about discovered tests from Deno.

    Method: deno/testModule

    Attributes:
        params: Test module parameters
        method: Fixed value "deno/testModule"
        jsonrpc: JSON-RPC version (always "2.0")
    """

    params: DenoTestModuleParams
    method: Literal["deno/testModule"] = DENO_TEST_MODULE
    jsonrpc: str = "2.0"


@define
class DenoTestModuleDeleteParams:
    """
    Parameters for the deno/testModuleDelete notification.

    Attributes:
        text_document: The document whose tests were deleted
    """

    text_document: lsp_type.TextDocumentIdentifier


@define
class DenoTestModuleDeleteNotification:
    """
    Notification about deleted tests from Deno.

    Method: deno/testModuleDelete

    Attributes:
        params: Test module delete parameters
        method: Fixed value "deno/testModuleDelete"
        jsonrpc: JSON-RPC version (always "2.0")
    """

    params: DenoTestModuleDeleteParams
    method: Literal["deno/testModuleDelete"] = DENO_TEST_MODULE_DELETE
    jsonrpc: str = "2.0"


@define
class DenoTestRunProgressParams:
    """
    Parameters for the deno/testRunProgress notification.

    Attributes:
        id: The test run ID
        message: Progress event (enqueued, started, passed, failed, errored, output, or end)
    """

    id: int
    message: DenoTestRunProgressMessage


@define
class DenoTestRunProgressNotification:
    """
    Notification about test run progress from Deno.

    Method: deno/testRunProgress

    Attributes:
        params: Test run progress parameters
        method: Fixed value "deno/testRunProgress"
        jsonrpc: JSON-RPC version (always "2.0")
    """

    params: DenoTestRunProgressParams
    method: Literal["deno/testRunProgress"] = DENO_TEST_RUN_PROGRESS
    jsonrpc: str = "2.0"


def register_hooks(converter: cattrs.Converter) -> None:
    resolve_types(DenoTestData)
    resolve_types(DenoTestIdentifier)
    resolve_types(DenoTestMessage)
    resolve_types(DenoTestEnqueuedStartedSkipped)
    resolve_types(DenoTestFailedErrored)
    resolve_types(DenoTestPassed)
    resolve_types(DenoTestOutput)
    resolve_types(DenoTestEnd)
    resolve_types(DenoEnqueuedTestModule)
    resolve_types(DenoCacheParams)
    resolve_types(DenoCacheRequest)
    resolve_types(DenoCacheResponse)
    resolve_types(DenoPerformanceRequest)
    resolve_types(DenoPerformanceResponse)
    resolve_types(DenoReloadImportRegistriesRequest)
    resolve_types(DenoReloadImportRegistriesResponse)
    resolve_types(DenoVirtualTextDocumentParams)
    resolve_types(DenoVirtualTextDocumentRequest)
    resolve_types(DenoVirtualTextDocumentResponse)
    resolve_types(DenoTaskParams)
    resolve_types(DenoTaskRequest)
    resolve_types(DenoTaskResponse)
    resolve_types(DenoTestRunRequestParams)
    resolve_types(DenoTestRunRequest)
    resolve_types(DenoTestRunResponseParams)
    resolve_types(DenoTestRunResponse)
    resolve_types(DenoTestRunCancelParams)
    resolve_types(DenoTestRunCancelRequest)
    resolve_types(DenoTestRunCancelResponse)
    resolve_types(DenoRegistryStatusNotificationParams)
    resolve_types(DenoRegistryStatusNotification)
    resolve_types(DenoTestModuleParams)
    resolve_types(DenoTestModuleNotification)
    resolve_types(DenoTestModuleDeleteParams)
    resolve_types(DenoTestModuleDeleteNotification)
    resolve_types(DenoTestRunProgressParams)
    resolve_types(DenoTestRunProgressNotification)

    def _test_run_progress_message_hook(
        obj: Any,  # noqa: ANN401
        _: type,
    ) -> DenoTestRunProgressMessage:
        if not isinstance(obj, dict):
            return obj

        match obj.get("type"):
            case "enqueued" | "started" | "skipped":
                return converter.structure(obj, DenoTestEnqueuedStartedSkipped)
            case "failed" | "errored":
                return converter.structure(obj, DenoTestFailedErrored)
            case "passed":
                return converter.structure(obj, DenoTestPassed)
            case "output":
                return converter.structure(obj, DenoTestOutput)
            case "end":
                return converter.structure(obj, DenoTestEnd)
            case _:
                raise ValueError(
                    f"Unknown DenoTestRunProgressMessage type: {obj.get('type')}"
                )

    converter.register_structure_hook(
        DenoTestRunProgressMessage, _test_run_progress_message_hook
    )


register_hooks(converters.get_converter())
