from __future__ import annotations

"""
Example integration tests for Client-Server interaction.

This file demonstrates the expected test structure for testing
interaction between clients and servers.
"""


class TestClientServerInitialization:
    """Tests for client-server initialization flow."""

    def test_client_class_has_required_methods(self):
        """Test that client class has required methods for initialization."""
        from lsp_client.client.abc import Client

        # Client should have the initialization flow methods
        assert hasattr(Client, "_initialize")
        assert hasattr(Client, "_shutdown")
        assert hasattr(Client, "_exit")

    def test_server_class_has_required_methods(self):
        """Test that server class has required methods for initialization."""
        from lsp_client.server.abc import Server

        # Server should have the initialization flow methods
        assert hasattr(Server, "request")
        assert hasattr(Server, "notify")


class TestNotificationFlow:
    """Tests for notification message flow."""

    def test_client_has_text_document_synchronize(self):
        """Test that client has text document synchronize capability."""
        from lsp_client.capability.notification import (
            WithNotifyTextDocumentSynchronize,
        )

        # WithNotifyTextDocumentSynchronize should exist
        assert WithNotifyTextDocumentSynchronize is not None

    def test_client_has_did_change_configuration(self):
        """Test that client has did change configuration capability."""
        from lsp_client.capability.notification import WithNotifyDidChangeConfiguration

        # WithNotifyDidChangeConfiguration should exist
        assert WithNotifyDidChangeConfiguration is not None


class TestRequestResponse:
    """Tests for request-response interactions."""

    def test_request_capabilities_exist(self):
        """Test that request capability mixins exist."""
        from lsp_client.capability.request import (
            WithRequestCompletion,
            WithRequestDefinition,
            WithRequestHover,
            WithRequestReferences,
        )

        assert WithRequestDefinition is not None
        assert WithRequestHover is not None
        assert WithRequestCompletion is not None
        assert WithRequestReferences is not None


class TestServerRequests:
    """Tests for server-initiated requests."""

    def test_server_request_capabilities_exist(self):
        """Test that server request capability mixins exist."""
        from lsp_client.capability.server_request import (
            WithRespondConfigurationRequest,
            WithRespondWorkspaceFoldersRequest,
        )

        assert WithRespondConfigurationRequest is not None
        assert WithRespondWorkspaceFoldersRequest is not None


class TestErrorHandling:
    """Tests for error handling in client-server interaction."""

    def test_json_rpc_exceptions_exist(self):
        """Test that JSON-RPC exception types exist."""
        from lsp_client.jsonrpc.exception import (
            JsonRpcError,
            JsonRpcParseError,
            JsonRpcResponseError,
            JsonRpcTransportError,
        )

        assert JsonRpcError is not None
        assert JsonRpcParseError is not None
        assert JsonRpcResponseError is not None
        assert JsonRpcTransportError is not None
