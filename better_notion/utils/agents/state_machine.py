"""State machine for managing task status transitions.

This module provides the state machine logic for task workflow transitions,
ensuring that tasks only move through valid states.
"""

from enum import Enum
from typing import Dict, List, Optional, Tuple


class TaskStatus(Enum):
    """Task status values following the workflow.

    The typical workflow is:
        Backlog → Claimed → In Progress → In Review → Completed

    Tasks can be Cancelled from most states.
    """

    BACKLOG = "Backlog"
    CLAIMED = "Claimed"
    IN_PROGRESS = "In Progress"
    IN_REVIEW = "In Review"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


class TaskStateMachine:
    """Manages valid task status transitions.

    This state machine enforces the workflow rules for task status changes.
    It prevents invalid transitions and provides helpers for querying
    possible next states.

    Example:
        >>> # Check if a transition is valid
        >>> is_valid = TaskStateMachine.can_transition(
        ...     TaskStatus.BACKLOG,
        ...     TaskStatus.CLAIMED
        ... )
        >>> print(is_valid)  # True

        >>> # Get next possible states
        >>> next_states = TaskStateMachine.get_next_statuses("Backlog")
        >>> print(next_states)  # ["Claimed", "Cancelled"]

        >>> # Validate transition
        >>> is_valid, error = TaskStateMachine.validate_transition(
        ...     "Backlog",
        ...     "Completed"
        ... )
        >>> print(error)  # "Invalid transition: Backlog → Completed"
    """

    # Define valid state transitions
    TRANSITIONS: Dict[TaskStatus, List[TaskStatus]] = {
        TaskStatus.BACKLOG: [
            TaskStatus.CLAIMED,
            TaskStatus.CANCELLED,
        ],
        TaskStatus.CLAIMED: [
            TaskStatus.IN_PROGRESS,
            TaskStatus.BACKLOG,  # Unclaim and return to backlog
            TaskStatus.CANCELLED,
        ],
        TaskStatus.IN_PROGRESS: [
            TaskStatus.IN_REVIEW,
            TaskStatus.COMPLETED,  # Skip review if not needed
            TaskStatus.CANCELLED,
        ],
        TaskStatus.IN_REVIEW: [
            TaskStatus.COMPLETED,
            TaskStatus.IN_PROGRESS,  # Request changes during review
            TaskStatus.CANCELLED,
        ],
        TaskStatus.COMPLETED: [
            # Terminal state - no transitions out
        ],
        TaskStatus.CANCELLED: [
            # Terminal state - no transitions out
        ],
    }

    @classmethod
    def can_transition(
        cls,
        from_status: TaskStatus,
        to_status: TaskStatus,
    ) -> bool:
        """Check if a transition between two states is valid.

        Args:
            from_status: Current state
            to_status: Desired next state

        Returns:
            True if the transition is valid, False otherwise

        Example:
            >>> TaskStateMachine.can_transition(
            ...     TaskStatus.BACKLOG,
            ...     TaskStatus.CLAIMED
            ... )
            True
        """
        allowed = cls.TRANSITIONS.get(from_status, [])
        return to_status in allowed

    @classmethod
    def validate_transition(
        cls,
        from_status: str,
        to_status: str,
    ) -> Tuple[bool, Optional[str]]:
        """Validate a transition and return (is_valid, error_message).

        This is a convenience method that handles string status values
        and returns a detailed error message if the transition is invalid.

        Args:
            from_status: Current status as string
            to_status: Desired next status as string

        Returns:
            Tuple of (is_valid, error_message):
            - is_valid: True if transition is valid
            - error_message: None if valid, error description if invalid

        Example:
            >>> is_valid, error = TaskStateMachine.validate_transition(
            ...     "Backlog",
            ...     "Claimed"
            ... )
            >>> print(is_valid)  # True
            >>> print(error)  # None

            >>> is_valid, error = TaskStateMachine.validate_transition(
            ...     "Completed",
            ...     "In Progress"
            ... )
            >>> print(is_valid)  # False
            >>> print(error)  # "Invalid transition: Completed → In Progress"
        """
        try:
            from_enum = TaskStatus(from_status)
            to_enum = TaskStatus(to_status)
        except ValueError as e:
            return False, f"Invalid status values: {from_status} → {to_status}"

        if not cls.can_transition(from_enum, to_enum):
            return False, f"Invalid transition: {from_status} → {to_status}"

        return True, None

    @classmethod
    def get_next_statuses(cls, current_status: str) -> List[str]:
        """Get list of valid next statuses from current status.

        Args:
            current_status: Current status as string

        Returns:
            List of valid next status values as strings

        Example:
            >>> TaskStateMachine.get_next_statuses("Backlog")
            ["Claimed", "Cancelled"]

            >>> TaskStateMachine.get_next_statuses("Completed")
            []
        """
        try:
            current_enum = TaskStatus(current_status)
            next_enums = cls.TRANSITIONS.get(current_enum, [])
            return [e.value for e in next_enums]
        except ValueError:
            return []

    @classmethod
    def is_terminal_state(cls, status: str) -> bool:
        """Check if a status is a terminal state (no transitions out).

        Terminal states are Completed and Cancelled.

        Args:
            status: Status to check

        Returns:
            True if status is terminal, False otherwise

        Example:
            >>> TaskStateMachine.is_terminal_state("Completed")
            True

            >>> TaskStateMachine.is_terminal_state("In Progress")
            False
        """
        try:
            status_enum = TaskStatus(status)
            allowed = cls.TRANSITIONS.get(status_enum, [])
            return len(allowed) == 0
        except ValueError:
            return False

    @classmethod
    def get_initial_state(cls) -> str:
        """Get the initial state for new tasks.

        Returns:
            The initial task status (Backlog)

    Example:
        >>> TaskStateMachine.get_initial_state()
        "Backlog"
        """
        return TaskStatus.BACKLOG.value
