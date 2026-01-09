from __future__ import annotations

import pytest

from lsp_client.capability.server_request import WithRespondConfigurationRequest
from lsp_client.clients import clients


@pytest.mark.parametrize("client_cls", clients.values())
def test_clients_have_default_configuration_method(client_cls):
    """Test that all clients have a create_default_config method."""
    assert hasattr(client_cls, "create_default_config"), (
        f"{client_cls.__name__} should have create_default_config method"
    )


@pytest.mark.parametrize("client_cls", clients.values())
def test_default_configuration_returns_valid_type(client_cls):
    """Test that create_default_config returns None or dict."""
    client = client_cls()
    result = client.create_default_config()
    assert result is None or isinstance(result, dict), (
        f"{client_cls.__name__}.create_default_config() should return None or dict"
    )


@pytest.mark.parametrize("client_cls", clients.values())
def test_clients_with_configuration_support_have_defaults(client_cls):
    """Test that clients supporting configuration have default configurations."""
    client = client_cls()

    # Check if client supports configuration request
    if not isinstance(client, WithRespondConfigurationRequest):
        pytest.skip(
            f"{client_cls.__name__} does not support WithRespondConfigurationRequest"
        )

    # Get default configuration
    config = client.create_default_config()

    # Clients with configuration support should have defaults
    # (especially those with inlay hints, diagnostics, etc.)
    assert config is not None, (
        f"{client_cls.__name__} supports configuration requests "
        f"and should provide default configuration"
    )

    # Verify it's a proper dict instance
    assert isinstance(config, dict)


@pytest.mark.parametrize("client_cls", clients.values())
def test_default_configuration_has_content(client_cls):
    """Test that default configurations contain actual settings."""
    client = client_cls()
    config = client.create_default_config()

    if config is None:
        pytest.skip(f"{client_cls.__name__} has no default configuration")

    # Check that the configuration dict has some content
    assert bool(config), (
        f"{client_cls.__name__} default configuration should not be empty"
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("client_cls", clients.values())
async def test_configuration_initialized_on_client_startup(client_cls):
    """Test that configuration is automatically initialized when client starts."""
    # This test would require actually starting the language server
    # For now, we just verify the client can be instantiated
    client = client_cls()

    # Check if client supports configuration
    if isinstance(client, WithRespondConfigurationRequest):
        # Before async context, config in ConfigurationMap should be empty
        assert not client.get_config_map().global_config


def test_rust_analyzer_default_config_has_inlay_hints():
    """Test that rust-analyzer default config enables inlay hints."""
    from lsp_client.clients.rust_analyzer import RustAnalyzerClient

    client = RustAnalyzerClient()
    config = client.create_default_config()

    assert config is not None
    assert config["rust-analyzer"]["inlayHints"]["enable"] is True


def test_gopls_default_config_has_hints():
    """Test that gopls default config enables hints."""
    from lsp_client.clients.gopls import GoplsClient

    client = GoplsClient()
    config = client.create_default_config()

    assert config is not None
    assert "hints" in config["gopls"]


def test_pyright_default_config_has_inlay_hints():
    """Test that pyright default config enables inlay hints."""
    from lsp_client.clients.pyright import PyrightClient

    client = PyrightClient()
    config = client.create_default_config()

    assert config is not None
    assert "inlayHints" in config["python"]["analysis"]


def test_typescript_default_config_has_inlay_hints():
    """Test that typescript-language-server default config enables inlay hints."""
    from lsp_client.clients.typescript import TypescriptClient

    client = TypescriptClient()
    config = client.create_default_config()

    assert config is not None
    assert "inlayHints" in config["typescript"]


def test_deno_default_config_has_inlay_hints():
    """Test that deno default config enables inlay hints."""
    from lsp_client.clients.deno import DenoClient

    client = DenoClient()
    config = client.create_default_config()

    assert config is not None
    assert "inlayHints" in config["deno"]


def test_pyrefly_default_config_has_inlay_hints():
    """Test that pyrefly default config enables inlay hints."""
    from lsp_client.clients.pyrefly import PyreflyClient

    client = PyreflyClient()
    config = client.create_default_config()

    assert config is not None
    assert "inlayHints" in config["pyrefly"]


def test_ty_default_config_has_diagnostics():
    """Test that ty default config enables diagnostics and completion."""
    from lsp_client.clients.ty import TyClient

    client = TyClient()
    config = client.create_default_config()

    assert config is not None
    assert "diagnostics" in config["ty"]
    assert "completion" in config["ty"]


def test_jdtls_default_config_has_java_settings():
    """Test that jdtls default config has java settings."""
    from lsp_client.clients.jdtls import JdtlsClient

    client = JdtlsClient()
    config = client.create_default_config()

    assert config is not None
    assert "java" in config
    assert config["java"]["autobuild"]["enabled"] is True
