"""
Tests for CLI configuration management.

This module tests the Config class and its methods for loading,
saving, and managing CLI configuration.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from better_notion._cli.config import Config


def test_config_get_config_path(tmp_path: Path) -> None:
    """Test that config path is correctly constructed."""
    # We can't easily mock Path.home(), so we just verify the method exists
    config_path = Config.get_config_path()
    assert config_path.name == "config.json"
    assert ".notion" in str(config_path)


def test_config_save(tmp_path: Path) -> None:
    """Test saving configuration to file."""
    # Use a temporary directory for testing
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Mock Path.home() to return temp directory
        import better_notion._cli.config as config_module

        original_home = Path.home

        def mock_home():
            return tmp_path

        Path.home = mock_home  # type: ignore

        try:
            config = Config.save(
                token="secret_test_token",
                timeout=60,
                retry_attempts=5,
            )

            # Verify config object
            assert config.token == "secret_test_token"
            assert config.timeout == 60
            assert config.retry_attempts == 5

            # Verify file was created
            config_file = tmp_path / ".notion" / "config.json"
            assert config_file.exists()

            # Verify file contents
            with open(config_file) as f:
                data = json.load(f)

            assert data["token"] == "secret_test_token"
            assert data["timeout"] == 60
            assert data["retry_attempts"] == 5

        finally:
            Path.home = original_home  # type: ignore


def test_config_load(tmp_path: Path) -> None:
    """Test loading configuration from file."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Mock Path.home() to return temp directory
        import better_notion._cli.config as config_module

        original_home = Path.home

        def mock_home():
            return tmp_path

        Path.home = mock_home  # type: ignore

        try:
            # Create config file
            config_dir = tmp_path / ".notion"
            config_dir.mkdir(parents=True, exist_ok=True)
            config_file = config_dir / "config.json"

            data = {
                "token": "secret_loaded_token",
                "timeout": 45,
                "retry_attempts": 3,
                "default_database": "db_abc123",
            }

            with open(config_file, "w") as f:
                json.dump(data, f)

            # Load config
            config = Config.load()

            assert config.token == "secret_loaded_token"
            assert config.timeout == 45
            assert config.retry_attempts == 3
            assert config.default_database == "db_abc123"

        finally:
            Path.home = original_home  # type: ignore


def test_config_load_missing_file(tmp_path: Path) -> None:
    """Test that loading missing config file raises Exit."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Mock Path.home() to return empty temp directory
        import better_notion._cli.config as config_module

        original_home = Path.home

        def mock_home():
            return tmp_path

        Path.home = mock_home  # type: ignore

        try:
            with pytest.raises(typer.Exit) as exc_info:
                Config.load()

            assert exc_info.value.exit_code == 1

        finally:
            Path.home = original_home  # type: ignore


def test_config_load_invalid_json(tmp_path: Path) -> None:
    """Test that loading invalid JSON raises Exit."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Mock Path.home() to return temp directory
        import better_notion._cli.config as config_module

        original_home = Path.home

        def mock_home():
            return tmp_path

        Path.home = mock_home  # type: ignore

        try:
            # Create invalid JSON file
            config_dir = tmp_path / ".notion"
            config_dir.mkdir(parents=True, exist_ok=True)
            config_file = config_dir / "config.json"

            with open(config_file, "w") as f:
                f.write("{invalid json")

            with pytest.raises(typer.Exit) as exc_info:
                Config.load()

            assert exc_info.value.exit_code == 1

        finally:
            Path.home = original_home  # type: ignore


def test_config_to_dict() -> None:
    """Test converting config to dictionary."""
    config = Config(
        token="secret_token",
        default_database="db_xyz",
        timeout=30,
        retry_attempts=3,
    )

    config_dict = config.to_dict()

    assert config_dict["token"] == "secret_token"
    assert config_dict["default_database"] == "db_xyz"
    assert config_dict["timeout"] == 30
    assert config_dict["retry_attempts"] == 3
    assert config_dict["default_output"] == "json"


def test_config_defaults() -> None:
    """Test that config has correct default values."""
    config = Config(token="secret_token")

    assert config.token == "secret_token"
    assert config.default_database is None
    assert config.default_output == "json"
    assert config.timeout == 30
    assert config.retry_attempts == 3


def test_config_save_without_token(tmp_path: Path) -> None:
    """Test that saving config without token raises Exit."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Mock Path.home() to return temp directory
        import better_notion._cli.config as config_module

        original_home = Path.home

        def mock_home():
            return tmp_path

        Path.home = mock_home  # type: ignore

        try:
            with pytest.raises(typer.Exit) as exc_info:
                Config.save(timeout=30)

            assert exc_info.value.exit_code == 1

        finally:
            Path.home = original_home  # type: ignore


# Import typer here to avoid issues with pytest
import typer
