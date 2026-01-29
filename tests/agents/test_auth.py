"""Unit tests for agent authentication system."""

import tempfile
from pathlib import Path

import pytest

from better_notion.utils.agents.auth import (
    AGENT_ID_FILE,
    AgentContext,
    clear_agent_id,
    get_agent_id_path,
    get_agent_info,
    get_or_create_agent_id,
    is_valid_agent_id,
    set_agent_id,
)


class TestAgentIdPath:
    """Tests for get_agent_id_path function."""

    def test_returns_path(self) -> None:
        """Test that get_agent_id_path returns a Path object."""
        path = get_agent_id_path()
        assert isinstance(path, Path)

    def test_path_ends_with_agent_id(self) -> None:
        """Test that path ends with 'agent_id'."""
        path = get_agent_id_path()
        assert path.name == "agent_id"


class TestGetOrCreateAgentId:
    """Tests for get_or_create_agent_id function."""

    def test_creates_new_agent_id(self) -> None:
        """Test that a new agent ID is created if none exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            import better_notion.utils.agents.auth as auth_module

            original_path = auth_module.AGENT_ID_FILE
            temp_file = Path(tmpdir) / "agent_id"
            auth_module.AGENT_ID_FILE = temp_file

            try:
                agent_id = get_or_create_agent_id()

                assert agent_id is not None
                assert agent_id.startswith("agent-")
                assert is_valid_agent_id(agent_id)

            finally:
                auth_module.AGENT_ID_FILE = original_path

    def test_reuses_existing_agent_id(self) -> None:
        """Test that existing agent ID is reused."""
        with tempfile.TemporaryDirectory() as tmpdir:
            import better_notion.utils.agents.auth as auth_module

            original_path = auth_module.AGENT_ID_FILE
            temp_file = Path(tmpdir) / "agent_id"
            auth_module.AGENT_ID_FILE = temp_file

            try:
                # Create agent ID
                first_id = get_or_create_agent_id()

                # Get it again
                second_id = get_or_create_agent_id()

                assert first_id == second_id

            finally:
                auth_module.AGENT_ID_FILE = original_path

    def test_saves_agent_id_to_file(self) -> None:
        """Test that agent ID is saved to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            import better_notion.utils.agents.auth as auth_module

            original_path = auth_module.AGENT_ID_FILE
            temp_file = Path(tmpdir) / "agent_id"
            auth_module.AGENT_ID_FILE = temp_file

            try:
                agent_id = get_or_create_agent_id()

                assert temp_file.exists()

                with open(temp_file, encoding="utf-8") as f:
                    content = f.read().strip()

                assert content == agent_id

            finally:
                auth_module.AGENT_ID_FILE = original_path


class TestSetAgentId:
    """Tests for set_agent_id function."""

    def test_sets_custom_agent_id(self) -> None:
        """Test setting a custom agent ID."""
        with tempfile.TemporaryDirectory() as tmpdir:
            import better_notion.utils.agents.auth as auth_module

            original_path = auth_module.AGENT_ID_FILE
            temp_file = Path(tmpdir) / "agent_id"
            auth_module.AGENT_ID_FILE = temp_file

            try:
                success = set_agent_id("agent-custom-123")

                assert success is True
                assert temp_file.exists()

                with open(temp_file, encoding="utf-8") as f:
                    content = f.read().strip()

                assert content == "agent-custom-123"

            finally:
                auth_module.AGENT_ID_FILE = original_path

    def test_overwrites_existing_agent_id(self) -> None:
        """Test that set_agent_id overwrites existing ID."""
        with tempfile.TemporaryDirectory() as tmpdir:
            import better_notion.utils.agents.auth as auth_module

            original_path = auth_module.AGENT_ID_FILE
            temp_file = Path(tmpdir) / "agent_id"
            auth_module.AGENT_ID_FILE = temp_file

            try:
                # Set initial ID
                set_agent_id("agent-first-123")

                # Overwrite with new ID
                set_agent_id("agent-second-456")

                with open(temp_file, encoding="utf-8") as f:
                    content = f.read().strip()

                assert content == "agent-second-456"

            finally:
                auth_module.AGENT_ID_FILE = original_path


class TestClearAgentId:
    """Tests for clear_agent_id function."""

    def test_clears_existing_agent_id(self) -> None:
        """Test clearing an existing agent ID."""
        with tempfile.TemporaryDirectory() as tmpdir:
            import better_notion.utils.agents.auth as auth_module

            original_path = auth_module.AGENT_ID_FILE
            temp_file = Path(tmpdir) / "agent_id"
            auth_module.AGENT_ID_FILE = temp_file

            try:
                # Create agent ID file
                set_agent_id("agent-test-123")

                assert temp_file.exists()

                # Clear it
                success = clear_agent_id()

                assert success is True
                assert not temp_file.exists()

            finally:
                auth_module.AGENT_ID_FILE = original_path

    def test_clear_nonexistent_agent_id(self) -> None:
        """Test clearing a non-existent agent ID file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            import better_notion.utils.agents.auth as auth_module

            original_path = auth_module.AGENT_ID_FILE
            temp_file = Path(tmpdir) / "agent_id"
            auth_module.AGENT_ID_FILE = temp_file

            try:
                # File doesn't exist
                assert not temp_file.exists()

                # Clear should still succeed
                success = clear_agent_id()

                assert success is True

            finally:
                auth_module.AGENT_ID_FILE = original_path


class TestIsValidAgentId:
    """Tests for is_valid_agent_id function."""

    def test_valid_agent_id(self) -> None:
        """Test validation of valid agent ID."""
        # Valid UUID format (hexadecimal only)
        valid_id = "agent-1a2b3c4d-5e6f-4a8b-9c0d-1e2f3a4b5c6d"
        assert is_valid_agent_id(valid_id) is True

    def test_invalid_agent_id_no_prefix(self) -> None:
        """Test that ID without 'agent-' prefix is invalid."""
        invalid_id = "1a2b3c4d-5e6f-7g8h-9i0j-1k2l3m4n5o6p"
        assert is_valid_agent_id(invalid_id) is False

    def test_invalid_agent_id_bad_uuid(self) -> None:
        """Test that ID with bad UUID is invalid."""
        invalid_id = "agent-not-a-uuid"
        assert is_valid_agent_id(invalid_id) is False

    def test_invalid_agent_id_empty_string(self) -> None:
        """Test that empty string is invalid."""
        assert is_valid_agent_id("") is False

    def test_valid_agent_id_lowercase_uuid(self) -> None:
        """Test that lowercase UUID is valid."""
        valid_id = "agent-1a2b3c4d-5e6f-4a8b-9c0d-1e2f3a4b5c6d"
        assert is_valid_agent_id(valid_id) is True

    def test_valid_agent_id_uppercase_uuid(self) -> None:
        """Test that uppercase UUID is valid."""
        valid_id = "agent-1A2B3C4D-5E6F-4A8B-9C0D-1E2F3A4B5C6D"
        assert is_valid_agent_id(valid_id) is True

    def test_valid_agent_id_mixed_case_uuid(self) -> None:
        """Test that mixed case UUID is valid."""
        valid_id = "agent-1a2B3c4D-5e6F-4a8B-9c0D-1e2F3a4B5c6D"
        assert is_valid_agent_id(valid_id) is True


class TestGetAgentInfo:
    """Tests for get_agent_info function."""

    def test_returns_agent_id(self) -> None:
        """Test that get_agent_info returns agent_id field."""
        with tempfile.TemporaryDirectory() as tmpdir:
            import better_notion.utils.agents.auth as auth_module

            original_path = auth_module.AGENT_ID_FILE
            temp_file = Path(tmpdir) / "agent_id"
            auth_module.AGENT_ID_FILE = temp_file

            try:
                info = get_agent_info()

                assert "agent_id" in info
                assert "agent_id_exists" in info
                assert "agent_id_path" in info

                assert is_valid_agent_id(info["agent_id"])

            finally:
                auth_module.AGENT_ID_FILE = original_path


class TestAgentContext:
    """Tests for AgentContext context manager."""

    def test_temporary_agent_id(self) -> None:
        """Test using a temporary agent ID within context."""
        with tempfile.TemporaryDirectory() as tmpdir:
            import better_notion.utils.agents.auth as auth_module

            original_path = auth_module.AGENT_ID_FILE
            temp_file = Path(tmpdir) / "agent_id"
            auth_module.AGENT_ID_FILE = temp_file

            try:
                # Set original ID
                original_id = "agent-original-123"
                set_agent_id(original_id)

                # Use temporary ID
                with AgentContext("agent-temp-456"):
                    current_id = get_or_create_agent_id()
                    assert current_id == "agent-temp-456"

                # After context, should be back to original
                final_id = get_or_create_agent_id()
                assert final_id == original_id

            finally:
                auth_module.AGENT_ID_FILE = original_path

    def test_restores_nonexistent_file(self) -> None:
        """Test that context cleans up temp file if original didn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            import better_notion.utils.agents.auth as auth_module

            original_path = auth_module.AGENT_ID_FILE
            temp_file = Path(tmpdir) / "agent_id"
            auth_module.AGENT_ID_FILE = temp_file

            try:
                # No original file
                assert not temp_file.exists()

                # Use temporary ID
                with AgentContext("agent-temp-789"):
                    assert temp_file.exists()
                    current_id = get_or_create_agent_id()
                    assert current_id == "agent-temp-789"

                # File should be cleaned up
                assert not temp_file.exists()

            finally:
                auth_module.AGENT_ID_FILE = original_path
