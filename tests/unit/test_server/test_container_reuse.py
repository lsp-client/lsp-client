from __future__ import annotations

"""
Unit tests for ContainerServer container reuse functionality.

Tests cover auto_remove flag, hash-based naming, container existence checking,
and mount validation.
"""

import pytest

from lsp_client.server.container import ContainerServer
from lsp_client.utils.workspace import Workspace, WorkspaceFolder


class TestContainerServerAutoRemove:
    """Tests for auto_remove flag functionality."""

    def test_auto_remove_default_true(self):
        """Test that auto_remove defaults to True."""
        server = ContainerServer(image="test-image")
        assert server.auto_remove is True

    def test_auto_remove_can_be_set_false(self):
        """Test that auto_remove can be set to False."""
        server = ContainerServer(image="test-image", auto_remove=False)
        assert server.auto_remove is False

    def test_format_args_includes_rm_when_auto_remove_true(self):
        """Test that --rm flag is included when auto_remove is True."""
        server = ContainerServer(image="test-image", auto_remove=True)
        workspace = Workspace(
            {
                "root": WorkspaceFolder(
                    uri="file:///test/path",
                    name="root",
                )
            }
        )
        args = server.format_args(workspace)
        assert "--rm" in args

    def test_format_args_excludes_rm_when_auto_remove_false(self):
        """Test that --rm flag is excluded when auto_remove is False."""
        server = ContainerServer(image="test-image", auto_remove=False)
        workspace = Workspace(
            {
                "root": WorkspaceFolder(
                    uri="file:///test/path",
                    name="root",
                )
            }
        )
        args = server.format_args(workspace)
        assert "--rm" not in args


class TestContainerServerHashNaming:
    """Tests for hash-based container naming."""

    def test_generate_hash_name_is_deterministic(self):
        """Test that hash name generation is deterministic."""
        server = ContainerServer(image="test-image")
        workspace = Workspace(
            {
                "root": WorkspaceFolder(
                    uri="file:///test/path",
                    name="root",
                )
            }
        )

        name1 = server._generate_hash_name(workspace)
        name2 = server._generate_hash_name(workspace)

        assert name1 == name2
        assert name1.startswith("lsp-server-")

    def test_generate_hash_name_differs_for_different_workspaces(self):
        """Test that different workspaces get different hash names."""
        server = ContainerServer(image="test-image")
        workspace1 = Workspace(
            {
                "root": WorkspaceFolder(
                    uri="file:///test/path1",
                    name="root",
                )
            }
        )
        workspace2 = Workspace(
            {
                "root": WorkspaceFolder(
                    uri="file:///test/path2",
                    name="root",
                )
            }
        )

        name1 = server._generate_hash_name(workspace1)
        name2 = server._generate_hash_name(workspace2)

        assert name1 != name2

    def test_generate_hash_name_differs_for_different_images(self):
        """Test that different images get different hash names."""
        server1 = ContainerServer(image="test-image-1")
        server2 = ContainerServer(image="test-image-2")
        workspace = Workspace(
            {
                "root": WorkspaceFolder(
                    uri="file:///test/path",
                    name="root",
                )
            }
        )

        name1 = server1._generate_hash_name(workspace)
        name2 = server2._generate_hash_name(workspace)

        assert name1 != name2

    def test_format_args_uses_hash_name_when_auto_remove_false(self):
        """Test that hash-based name is used when auto_remove is False."""
        server = ContainerServer(image="test-image", auto_remove=False)
        workspace = Workspace(
            {
                "root": WorkspaceFolder(
                    uri="file:///test/path",
                    name="root",
                )
            }
        )

        args = server.format_args(workspace)
        expected_name = server._generate_hash_name(workspace)

        assert "--name" in args
        name_index = args.index("--name")
        assert args[name_index + 1] == expected_name

    def test_format_args_prefers_custom_name_over_hash(self):
        """Test that custom container_name takes precedence over hash."""
        server = ContainerServer(
            image="test-image", auto_remove=False, container_name="my-custom-name"
        )
        workspace = Workspace(
            {
                "root": WorkspaceFolder(
                    uri="file:///test/path",
                    name="root",
                )
            }
        )

        args = server.format_args(workspace)

        assert "--name" in args
        name_index = args.index("--name")
        assert args[name_index + 1] == "my-custom-name"


class TestWorkspaceId:
    """Tests for workspace ID generation."""

    def test_workspace_id_is_deterministic(self):
        """Test that workspace ID is deterministic."""
        workspace = Workspace(
            {
                "root": WorkspaceFolder(
                    uri="file:///test/path",
                    name="root",
                )
            }
        )

        id1 = workspace.id
        id2 = workspace.id

        assert id1 == id2
        assert isinstance(id1, str)
        assert len(id1) > 0

    def test_workspace_id_differs_for_different_workspaces(self):
        """Test that different workspaces have different IDs."""
        workspace1 = Workspace(
            {
                "root": WorkspaceFolder(
                    uri="file:///test/path1",
                    name="root",
                )
            }
        )
        workspace2 = Workspace(
            {
                "root": WorkspaceFolder(
                    uri="file:///test/path2",
                    name="root",
                )
            }
        )

        assert workspace1.id != workspace2.id

    def test_workspace_id_same_for_same_folders_different_order(self):
        """Test that workspace ID is consistent regardless of folder order."""
        workspace1 = Workspace(
            {
                "folder1": WorkspaceFolder(
                    uri="file:///test/path1",
                    name="folder1",
                ),
                "folder2": WorkspaceFolder(
                    uri="file:///test/path2",
                    name="folder2",
                ),
            }
        )
        workspace2 = Workspace(
            {
                "folder2": WorkspaceFolder(
                    uri="file:///test/path2",
                    name="folder2",
                ),
                "folder1": WorkspaceFolder(
                    uri="file:///test/path1",
                    name="folder1",
                ),
            }
        )

        # Should be the same because items are sorted before hashing
        assert workspace1.id == workspace2.id


class TestContainerServerMountTargets:
    """Tests for getting expected mount targets."""

    def test_get_expected_mount_targets_for_workspace_folders(self):
        """Test that workspace folders are included in expected mount targets."""
        server = ContainerServer(image="test-image")
        workspace = Workspace(
            {
                "root": WorkspaceFolder(
                    uri="file:///test/path",
                    name="root",
                )
            }
        )

        targets = server._get_expected_mount_targets(workspace)

        # Should include the workspace folder path
        assert len(targets) > 0
        assert isinstance(targets, set)

    def test_get_expected_mount_targets_includes_extra_mounts(self):
        """Test that extra mounts are included in expected targets."""
        from pathlib import Path

        from lsp_client.server.container import BindMount

        extra_mount = BindMount(source="/host/path", target="/container/path")
        server = ContainerServer(image="test-image", mounts=[extra_mount])
        workspace = Workspace(
            {
                "root": WorkspaceFolder(
                    uri="file:///test/path",
                    name="root",
                )
            }
        )

        targets = server._get_expected_mount_targets(workspace)

        assert "/container/path" in targets
