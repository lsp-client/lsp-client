from __future__ import annotations

from lsp_client.capability.build import build_client_capabilities
from lsp_client.capability.notification.text_document_synchronize import (
    WithNotifyTextDocumentSynchronize,
)
from lsp_client.capability.request.definition import WithRequestDefinition
from lsp_client.capability.request.hover import WithRequestHover


def test_mixin_hover():
    class HoverClient(WithRequestHover):
        pass

    capabilities = build_client_capabilities(HoverClient)
    assert capabilities.text_document is not None
    assert capabilities.text_document.hover is not None


def test_mixin_definition():
    class DefinitionClient(WithRequestDefinition):
        pass

    capabilities = build_client_capabilities(DefinitionClient)
    assert capabilities.text_document is not None
    assert capabilities.text_document.definition is not None


def test_mixin_synchronization():
    class SyncClient(WithNotifyTextDocumentSynchronize):
        pass

    capabilities = build_client_capabilities(SyncClient)
    assert capabilities.text_document is not None
    assert capabilities.text_document.synchronization is not None
    assert capabilities.text_document.synchronization.did_save is True
