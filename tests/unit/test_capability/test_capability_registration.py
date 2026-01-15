from __future__ import annotations

from contextlib import asynccontextmanager

import pytest

from lsp_client.capability.server_request.capability_registration import (
    WithRespondCapabilityRegistration,
)
from lsp_client.utils.types import lsp_type


class TestWithRespondCapabilityRegistration:
    def test_capability_imports(self):
        assert WithRespondCapabilityRegistration is not None

    def test_capability_iterates_methods(self):
        methods = list(WithRespondCapabilityRegistration.iter_methods())
        assert lsp_type.CLIENT_REGISTER_CAPABILITY in methods
        assert lsp_type.CLIENT_UNREGISTER_CAPABILITY in methods

    def test_capability_is_protocol(self):
        assert hasattr(WithRespondCapabilityRegistration, "__subclasshook__")

    @pytest.mark.asyncio
    async def test_respond_register_capability(self):
        class MockClient(WithRespondCapabilityRegistration):
            def get_document_state(self):
                pass

            def get_workspace(self):
                pass

            def get_config_map(self):
                pass

            @classmethod
            def get_language_config(cls):
                pass

            @asynccontextmanager
            async def open_files(self, *file_paths):
                yield

            async def request(self, req, schema):
                pass

            async def notify(self, msg):
                pass

            async def write_file(self, uri, content):
                pass

        client = MockClient()
        req = lsp_type.RegistrationRequest(
            id="1", params=lsp_type.RegistrationParams(registrations=[])
        )
        resp = await client.respond_register_capability(req)
        assert resp.id == "1"
        assert resp.result is None

    @pytest.mark.asyncio
    async def test_respond_unregister_capability(self):
        class MockClient(WithRespondCapabilityRegistration):
            def get_document_state(self):
                pass

            def get_workspace(self):
                pass

            def get_config_map(self):
                pass

            @classmethod
            def get_language_config(cls):
                pass

            @asynccontextmanager
            async def open_files(self, *file_paths):
                yield

            async def request(self, req, schema):
                pass

            async def notify(self, msg):
                pass

            async def write_file(self, uri, content):
                pass

        client = MockClient()
        req = lsp_type.UnregistrationRequest(
            id="1", params=lsp_type.UnregistrationParams(unregisterations=[])
        )
        resp = await client.respond_unregister_capability(req)
        assert resp.id == "1"
        assert resp.result is None
