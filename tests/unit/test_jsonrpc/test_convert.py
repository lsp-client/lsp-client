from __future__ import annotations

"""
Example unit tests for JSON-RPC module.

This file demonstrates the expected test structure for testing
JSON-RPC serialization, deserialization, and error handling.
"""


class TestJsonRpcConvert:
    """Tests for JSON-RPC conversion functions."""

    def test_request_serialize(self):
        """Test that request serialization works."""
        from lsp_client.jsonrpc.convert import request_serialize
        from lsp_client.utils.types import lsp_type

        request = lsp_type.InitializeRequest(
            id="initialize",
            params=lsp_type.InitializeParams(
                capabilities=lsp_type.ClientCapabilities(),
                process_id=None,
            ),
        )
        result = request_serialize(request)
        assert result["jsonrpc"] == "2.0"
        assert result["id"] == "initialize"
        assert result["method"] == "initialize"

    def test_notification_serialize(self):
        """Test that notification serialization works."""
        from lsp_client.jsonrpc.convert import notification_serialize
        from lsp_client.utils.types import lsp_type

        notification = lsp_type.InitializedNotification(
            params=lsp_type.InitializedParams()
        )
        result = notification_serialize(notification)
        assert result["jsonrpc"] == "2.0"
        assert result["method"] == "initialized"

    def test_response_deserialize_success(self):
        """Test that successful response deserialization works."""
        from lsp_client.jsonrpc.convert import response_deserialize
        from lsp_client.jsonrpc.types import RawResponse
        from lsp_client.utils.types import lsp_type

        raw_response = RawResponse(
            jsonrpc="2.0",
            id="1",
            result={"capabilities": {}},
        )
        result = response_deserialize(raw_response, lsp_type.InitializeResponse)
        assert isinstance(result, lsp_type.InitializeResult)

    def test_response_deserialize_error(self):
        """Test that error response raises exception."""
        from lsp_client.jsonrpc.convert import response_deserialize
        from lsp_client.jsonrpc.exception import JsonRpcResponseError
        from lsp_client.jsonrpc.types import RawError
        from lsp_client.utils.types import lsp_type

        raw_error_response = RawError(
            jsonrpc="2.0",
            id="1",
            error={
                "code": -32600,
                "message": "Invalid Request",
            },
        )
        try:
            response_deserialize(raw_error_response, lsp_type.InitializeResponse)
            assert False, "Should have raised JsonRpcResponseError"
        except JsonRpcResponseError:
            pass


class TestJsonRpcException:
    """Tests for JSON-RPC exceptions."""

    def test_json_rpc_parse_error(self):
        """Test JsonRpcParseError."""
        from lsp_client.jsonrpc.exception import JsonRpcParseError

        error = JsonRpcParseError("Test error")
        assert "Test error" in str(error)

    def test_json_rpc_response_error(self):
        """Test JsonRpcResponseError."""
        from lsp_client.jsonrpc.exception import JsonRpcResponseError

        error = JsonRpcResponseError(
            code=-32600,
            message="Invalid Request",
            data=None,
        )
        assert error.code == -32600
        assert error.message == "Invalid Request"

    def test_json_rpc_transport_error(self):
        """Test JsonRpcTransportError."""
        from lsp_client.jsonrpc.exception import JsonRpcTransportError

        error = JsonRpcTransportError("Connection lost")
        assert "Connection lost" in str(error)


class TestJsonRpcTypes:
    """Tests for JSON-RPC type definitions."""

    def test_raw_request_type(self):
        """Test RawRequest type structure."""
        from lsp_client.jsonrpc.types import RawRequest

        request: RawRequest = {
            "jsonrpc": "2.0",
            "id": "1",
            "method": "test",
            "params": {},
        }
        assert request["jsonrpc"] == "2.0"

    def test_raw_notification_type(self):
        """Test RawNotification type structure."""
        from lsp_client.jsonrpc.types import RawNotification

        notification: RawNotification = {
            "jsonrpc": "2.0",
            "method": "test",
            "params": {},
        }
        assert notification["jsonrpc"] == "2.0"

    def test_raw_response_type(self):
        """Test RawResponsePackage type structure."""

        response = {
            "jsonrpc": "2.0",
            "id": "1",
            "result": {},
        }
        assert response["jsonrpc"] == "2.0"
