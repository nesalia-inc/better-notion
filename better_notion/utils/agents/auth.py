"""Agent authentication and identification for the agents workflow system.

This module provides agent identification and tracking functionality. Each agent
gets a unique ID that is stored locally and used for tracking operations across
workflow commands.
"""

import json
import uuid
from pathlib import Path
from typing import Optional


# Default path for agent ID storage
AGENT_ID_FILE = Path.home() / ".notion" / "agent_id"


def get_agent_id_path() -> Path:
    """Get the path to the agent ID file.

    Returns:
        Path to the agent ID file

    Example:
        >>> path = get_agent_id_path()
        >>> print(path)
        PosixPath('/Users/user/.notion/agent_id')
    """
    return AGENT_ID_FILE


def get_or_create_agent_id() -> str:
    """Get existing agent ID or create a new one.

    This function checks if an agent ID file exists in ~/.notion/agent_id.
    If it exists, it reads and returns the ID. If not, it generates a new
    UUID-based agent ID and stores it.

    Returns:
        Agent ID string (format: "agent-{uuid}")

    Example:
        >>> agent_id = get_or_create_agent_id()
        >>> print(agent_id)
        'agent-1a2b3c4d-5e6f-7g8h-9i0j-1k2l3m4n5o6p'
    """
    # Ensure directory exists
    AGENT_ID_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Check if agent ID file exists
    if AGENT_ID_FILE.exists() and AGENT_ID_FILE.is_file():
        try:
            with open(AGENT_ID_FILE, encoding="utf-8") as f:
                content = f.read().strip()

            if content:
                return content

        except (IOError, OSError):
            # File exists but can't be read
            # Fall through to create new ID
            pass

    # Generate new agent ID
    agent_id = f"agent-{uuid.uuid4()}"

    # Save to file
    try:
        with open(AGENT_ID_FILE, "w", encoding="utf-8") as f:
            f.write(agent_id)
    except (IOError, OSError) as e:
        # Can't save agent ID - log warning but continue
        # The agent can still function with a temporary ID
        pass

    return agent_id


def set_agent_id(agent_id: str) -> bool:
    """Set a specific agent ID (useful for testing or manual configuration).

    Args:
        agent_id: Agent ID to set

    Returns:
        True if agent ID was saved successfully, False otherwise

    Example:
        >>> success = set_agent_id("agent-custom-id-123")
        >>> print(success)
        True
    """
    # Ensure directory exists
    AGENT_ID_FILE.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(AGENT_ID_FILE, "w", encoding="utf-8") as f:
            f.write(agent_id.strip())

        return True

    except (IOError, OSError):
        return False


def clear_agent_id() -> bool:
    """Clear the stored agent ID.

    This is useful for testing or when you want to generate a fresh agent ID.

    Returns:
        True if agent ID was cleared successfully, False otherwise

    Example:
        >>> clear_agent_id()
        True
        >>> new_id = get_or_create_agent_id()
        >>> # Will generate a new ID
    """
    try:
        if AGENT_ID_FILE.exists():
            AGENT_ID_FILE.unlink()

        return True

    except (IOError, OSError):
        return False


def is_valid_agent_id(agent_id: str) -> bool:
    """Check if a string is a valid agent ID format.

    Valid agent IDs must start with "agent-" followed by a UUID.

    Args:
        agent_id: Agent ID string to validate

    Returns:
        True if agent ID is valid format, False otherwise

    Example:
        >>> is_valid_agent_id("agent-1a2b3c4d-5e6f-7g8h-9i0j-1k2l3m4n5o6p")
        True

        >>> is_valid_agent_id("invalid-id")
        False
    """
    if not agent_id.startswith("agent-"):
        return False

    # Extract UUID part
    uuid_part = agent_id[6:]  # Remove "agent-" prefix

    try:
        # Try to parse as UUID
        uuid.UUID(uuid_part)
        return True

    except ValueError:
        return False


def get_agent_info() -> dict[str, str]:
    """Get complete agent information including ID and metadata.

    Returns:
        Dict with agent information:
        - agent_id: The agent's unique identifier
        - agent_id_exists: Whether the agent ID file exists
        - agent_id_path: Path to the agent ID file

    Example:
        >>> info = get_agent_info()
        >>> print(info['agent_id'])
        'agent-1a2b3c4d-5e6f-7g8h-9i0j-1k2l3m4n5o6p'
    """
    return {
        "agent_id": get_or_create_agent_id(),
        "agent_id_exists": AGENT_ID_FILE.exists(),
        "agent_id_path": str(AGENT_ID_FILE),
    }


class AgentContext:
    """Context manager for temporary agent ID overrides.

    This is useful for testing when you want to temporarily use a different
    agent ID without affecting the stored ID.

    Example:
        >>> with AgentContext("agent-test-123"):
        ...     agent_id = get_or_create_agent_id()
        ...     print(agent_id)  # "agent-test-123"
        >>> # Back to normal agent ID
    """

    def __init__(self, temp_agent_id: str):
        """Initialize the context manager.

        Args:
            temp_agent_id: Temporary agent ID to use during context
        """
        self.temp_agent_id = temp_agent_id
        self.original_id: Optional[str] = None
        self.file_existed: bool = False

    def __enter__(self) -> "AgentContext":
        """Enter the context and save original agent ID."""
        # Save original ID if file exists
        if AGENT_ID_FILE.exists():
            self.file_existed = True
            try:
                with open(AGENT_ID_FILE, encoding="utf-8") as f:
                    self.original_id = f.read().strip()
            except (IOError, OSError):
                self.original_id = None

        # Set temporary ID
        set_agent_id(self.temp_agent_id)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit the context and restore original agent ID."""
        if self.original_id:
            # Restore original ID
            set_agent_id(self.original_id)
        elif self.file_existed:
            # File existed but couldn't read - clear it
            clear_agent_id()
        else:
            # File didn't exist - remove the temp file
            clear_agent_id()

        return None
