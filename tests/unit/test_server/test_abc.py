from __future__ import annotations

"""
Example unit tests for Server module.

This file demonstrates the expected test structure for testing
the Server abstract base class and its implementations.
"""


class TestLocalServer:
    """Tests for LocalServer implementation."""

    def test_local_server_requires_program(self):
        """Test that LocalServer requires program parameter."""
        from lsp_client.server.local import LocalServer

        # Should not raise - program is required
        server = LocalServer(program="test-program")
        assert server.program == "test-program"

    def test_local_server_default_args(self):
        """Test that LocalServer has default args."""
        from lsp_client.server.local import LocalServer

        server = LocalServer(program="test-program")
        assert server.args == []

    def test_local_server_has_env(self):
        """Test that LocalServer has env parameter."""
        from lsp_client.server.local import LocalServer

        server = LocalServer(program="test-program", env={"TEST": "value"})
        assert server.env == {"TEST": "value"}

    def test_local_server_has_shutdown_timeout(self):
        """Test that LocalServer has shutdown_timeout."""
        from lsp_client.server.local import LocalServer

        server = LocalServer(program="test-program")
        assert hasattr(server, "shutdown_timeout")
        assert server.shutdown_timeout == 5.0


class TestContainerServer:
    """Tests for ContainerServer implementation."""

    def test_container_server_requires_image(self):
        """Test that ContainerServer requires image parameter."""
        from lsp_client.server.container import ContainerServer

        server = ContainerServer(image="test-image")
        assert server.image == "test-image"

    def test_container_server_no_workdir(self):
        """Test that ContainerServer no longer has workdir attribute."""
        from lsp_client.server.container import ContainerServer

        server = ContainerServer(image="test-image")
        assert not hasattr(server, "workdir")

    def test_container_server_default_backend(self):
        """Test that ContainerServer has default backend."""
        from lsp_client.server.container import ContainerServer

        server = ContainerServer(image="test-image")
        assert server.backend == "docker"

    def test_container_server_has_mounts(self):
        """Test that ContainerServer has mounts parameter."""
        from lsp_client.server.container import ContainerServer

        server = ContainerServer(image="test-image")
        assert hasattr(server, "mounts")
        assert server.mounts == []

    def test_container_server_extra_container_args(self):
        """Test that ContainerServer has extra_container_args."""
        from lsp_client.server.container import ContainerServer

        server = ContainerServer(image="test-image", extra_container_args=["--arg"])
        assert server.extra_container_args == ["--arg"]
