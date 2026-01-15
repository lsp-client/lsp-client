from __future__ import annotations

from typing import Final

from ..diagnostic.workspace import WithWorkspaceDiagnostic
from .apply_edit import WithRespondApplyEdit
from .capability_registration import WithRespondCapabilityRegistration
from .configuration import WithRespondConfigurationRequest
from .inlay_hint_refresh import WithRespondInlayHintRefresh
from .show_document_request import WithRespondShowDocumentRequest
from .show_message_request import WithRespondShowMessageRequest
from .workspace_folders import WithRespondWorkspaceFoldersRequest

capabilities: Final = (
    WithRespondApplyEdit,
    WithRespondConfigurationRequest,
    WithWorkspaceDiagnostic,
    WithRespondInlayHintRefresh,
    WithRespondShowDocumentRequest,
    WithRespondShowMessageRequest,
    WithRespondWorkspaceFoldersRequest,
    WithRespondCapabilityRegistration,
)

__all__ = [
    "WithRespondApplyEdit",
    "WithRespondCapabilityRegistration",
    "WithRespondConfigurationRequest",
    "WithRespondInlayHintRefresh",
    "WithRespondShowDocumentRequest",
    "WithRespondShowMessageRequest",
    "WithRespondWorkspaceFoldersRequest",
    "WithWorkspaceDiagnostic",
    "capabilities",
]
