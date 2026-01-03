from __future__ import annotations

from attrs import frozen

from .container import ContainerServer
from .local import LocalServer


@frozen
class DefaultServers:
    """
    Container for default server runtimes.

    Provides access to both local and containerized server implementations
    that can be used as fallback when no explicit server is configured.

    Attributes:
        local: LocalServer instance for running server as subprocess
        container: ContainerServer instance for running server in container

    Example:
        servers = DefaultServers(
            local=LocalServer(program="pyright"),
            container=ContainerServer(image="pyright:latest")
        )
    """

    local: LocalServer
    container: ContainerServer
