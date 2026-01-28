from __future__ import annotations

import shutil
import sys
import tempfile
from collections.abc import Sequence
from pathlib import Path
from subprocess import CalledProcessError
from typing import TypedDict

import anyio
import httpx
from loguru import logger

from lsp_client.server import ServerInstallationError


class ShellInfo(TypedDict):
    """
    Information about the platform's shell and script extension.
    """

    shell: str
    extension: str


def _get_platform_shell() -> ShellInfo:
    """Return the system shell and its script extension."""
    match sys.platform:
        case "win32":
            if shutil.which("powershell"):
                return ShellInfo(shell="powershell", extension=".ps1")
            return ShellInfo(shell="cmd", extension=".bat")
        case _:
            if shutil.which("bash"):
                return ShellInfo(shell="bash", extension=".sh")
            return ShellInfo(shell="sh", extension=".sh")


async def install_via_commands(
    binary: str,
    commands: Sequence[str],
    *,
    error_message: str,
) -> None:
    """
    Install a binary by executing a sequence of commands.

    Args:
        binary: The name of the binary to install.
        commands: The commands to execute.
        error_message: Detailed message to show if installation fails.
    """
    if shutil.which(binary):
        return

    logger.warning(f"{binary} not found, attempting to install...")
    try:
        await anyio.run_process(commands)
        logger.info(f"Successfully installed {binary}")
    except CalledProcessError as e:
        msg = f"Installation of {binary} failed. {error_message}"
        raise ServerInstallationError(msg) from e


async def install_via_script(
    binary: str,
    script_url: str,
    *,
    error_message: str,
) -> None:
    """
    Install a binary by downloading and executing a script.

    Args:
        binary: The name of the binary to install.
        script_url: The URL to download the installation script from.
        error_message: Detailed message to show if installation fails.
    """
    if shutil.which(binary):
        return

    logger.warning(f"{binary} not found, attempting to install...")

    try:
        info = _get_platform_shell()
        shell = info["shell"]
        ext = info["extension"]

        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(script_url)
            response.raise_for_status()
            script_content = response.text

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=ext, delete=False
        ) as tmp_file:
            tmp_file.write(script_content)
            tmp_path = Path(tmp_file.name)

        try:
            if sys.platform != "win32":
                tmp_path.chmod(0o755)

            match (sys.platform, shell):
                case ("win32", "powershell"):
                    command = [
                        "powershell",
                        "-ExecutionPolicy",
                        "Bypass",
                        "-File",
                        str(tmp_path),
                    ]
                case _:
                    command = [shell, str(tmp_path)]

            logger.debug(f"Executing installation script with: {' '.join(command)}")
            await anyio.run_process(command)
            logger.info(f"Successfully installed {binary}")
        finally:
            tmp_path.unlink(missing_ok=True)

    except httpx.HTTPError as e:
        msg = (
            f"Failed to download installation script from {script_url}. {error_message}"
        )
        raise ServerInstallationError(msg) from e
    except CalledProcessError as e:
        msg = f"Installation of {binary} failed. {error_message}"
        raise ServerInstallationError(msg) from e
