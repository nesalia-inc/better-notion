"""Unit tests for task state machine."""

import pytest

from better_notion.utils.agents.state_machine import (
    TaskStatus,
    TaskStateMachine,
)


class TestTaskStatus:
    """Tests for TaskStatus enum."""

    def test_status_values(self) -> None:
        """Test that all status values are correctly defined."""
        assert TaskStatus.BACKLOG.value == "Backlog"
        assert TaskStatus.CLAIMED.value == "Claimed"
        assert TaskStatus.IN_PROGRESS.value == "In Progress"
        assert TaskStatus.IN_REVIEW.value == "In Review"
        assert TaskStatus.COMPLETED.value == "Completed"
        assert TaskStatus.CANCELLED.value == "Cancelled"


class TestTaskStateMachine:
    """Tests for TaskStateMachine class."""

    def test_valid_transition_backlog_to_claimed(self) -> None:
        """Test valid transition from Backlog to Claimed."""
        assert TaskStateMachine.can_transition(
            TaskStatus.BACKLOG,
            TaskStatus.CLAIMED,
        ) is True

    def test_valid_transition_claimed_to_in_progress(self) -> None:
        """Test valid transition from Claimed to In Progress."""
        assert TaskStateMachine.can_transition(
            TaskStatus.CLAIMED,
            TaskStatus.IN_PROGRESS,
        ) is True

    def test_valid_transition_in_progress_to_in_review(self) -> None:
        """Test valid transition from In Progress to In Review."""
        assert TaskStateMachine.can_transition(
            TaskStatus.IN_PROGRESS,
            TaskStatus.IN_REVIEW,
        ) is True

    def test_valid_transition_in_review_to_completed(self) -> None:
        """Test valid transition from In Review to Completed."""
        assert TaskStateMachine.can_transition(
            TaskStatus.IN_REVIEW,
            TaskStatus.COMPLETED,
        ) is True

    def test_valid_transition_in_progress_to_completed(self) -> None:
        """Test valid transition from In Progress to Completed (skip review)."""
        assert TaskStateMachine.can_transition(
            TaskStatus.IN_PROGRESS,
            TaskStatus.COMPLETED,
        ) is True

    def test_valid_transition_in_review_to_in_progress(self) -> None:
        """Test valid transition from In Review back to In Progress (changes requested)."""
        assert TaskStateMachine.can_transition(
            TaskStatus.IN_REVIEW,
            TaskStatus.IN_PROGRESS,
        ) is True

    def test_valid_transition_claimed_to_backlog(self) -> None:
        """Test valid transition from Claimed back to Backlog (unclaim)."""
        assert TaskStateMachine.can_transition(
            TaskStatus.CLAIMED,
            TaskStatus.BACKLOG,
        ) is True

    def test_valid_transition_to_cancelled(self) -> None:
        """Test that Cancelled can be reached from multiple states."""
        # From Backlog
        assert TaskStateMachine.can_transition(
            TaskStatus.BACKLOG,
            TaskStatus.CANCELLED,
        ) is True

        # From Claimed
        assert TaskStateMachine.can_transition(
            TaskStatus.CLAIMED,
            TaskStatus.CANCELLED,
        ) is True

        # From In Progress
        assert TaskStateMachine.can_transition(
            TaskStatus.IN_PROGRESS,
            TaskStatus.CANCELLED,
        ) is True

        # From In Review
        assert TaskStateMachine.can_transition(
            TaskStatus.IN_REVIEW,
            TaskStatus.CANCELLED,
        ) is True

    def test_invalid_transition_backlog_to_in_progress(self) -> None:
        """Test invalid transition from Backlog to In Progress (must claim first)."""
        assert TaskStateMachine.can_transition(
            TaskStatus.BACKLOG,
            TaskStatus.IN_PROGRESS,
        ) is False

    def test_invalid_transition_backlog_to_completed(self) -> None:
        """Test invalid transition from Backlog to Completed."""
        assert TaskStateMachine.can_transition(
            TaskStatus.BACKLOG,
            TaskStatus.COMPLETED,
        ) is False

    def test_invalid_transition_completed_to_in_progress(self) -> None:
        """Test invalid transition from Completed back to In Progress."""
        assert TaskStateMachine.can_transition(
            TaskStatus.COMPLETED,
            TaskStatus.IN_PROGRESS,
        ) is False

    def test_invalid_transition_cancelled_to_backlog(self) -> None:
        """Test invalid transition from Cancelled back to Backlog."""
        assert TaskStateMachine.can_transition(
            TaskStatus.CANCELLED,
            TaskStatus.BACKLOG,
        ) is False

    def test_validate_transition_valid(self) -> None:
        """Test validate_transition with valid transition."""
        is_valid, error = TaskStateMachine.validate_transition(
            "Backlog",
            "Claimed",
        )

        assert is_valid is True
        assert error is None

    def test_validate_transition_invalid(self) -> None:
        """Test validate_transition with invalid transition."""
        is_valid, error = TaskStateMachine.validate_transition(
            "Backlog",
            "Completed",
        )

        assert is_valid is False
        assert error == "Invalid transition: Backlog → Completed"

    def test_validate_transition_invalid_status(self) -> None:
        """Test validate_transition with invalid status values."""
        is_valid, error = TaskStateMachine.validate_transition(
            "InvalidStatus",
            "Claimed",
        )

        assert is_valid is False
        assert "Invalid status values" in error

    def test_get_next_statuses_backlog(self) -> None:
        """Test get_next_statuses for Backlog."""
        next_states = TaskStateMachine.get_next_statuses("Backlog")

        assert set(next_states) == {"Claimed", "Cancelled"}

    def test_get_next_statuses_claimed(self) -> None:
        """Test get_next_statuses for Claimed."""
        next_states = TaskStateMachine.get_next_statuses("Claimed")

        assert set(next_states) == {"In Progress", "Backlog", "Cancelled"}

    def test_get_next_statuses_in_progress(self) -> None:
        """Test get_next_statuses for In Progress."""
        next_states = TaskStateMachine.get_next_statuses("In Progress")

        assert set(next_states) == {"In Review", "Completed", "Cancelled"}

    def test_get_next_statuses_in_review(self) -> None:
        """Test get_next_statuses for In Review."""
        next_states = TaskStateMachine.get_next_statuses("In Review")

        assert set(next_states) == {"Completed", "In Progress", "Cancelled"}

    def test_get_next_statuses_completed(self) -> None:
        """Test get_next_statuses for Completed (terminal state)."""
        next_states = TaskStateMachine.get_next_statuses("Completed")

        assert next_states == []

    def test_get_next_statuses_cancelled(self) -> None:
        """Test get_next_statuses for Cancelled (terminal state)."""
        next_states = TaskStateMachine.get_next_statuses("Cancelled")

        assert next_states == []

    def test_get_next_statuses_invalid_status(self) -> None:
        """Test get_next_statuses with invalid status."""
        next_states = TaskStateMachine.get_next_statuses("Invalid")

        assert next_states == []

    def test_is_terminal_state_completed(self) -> None:
        """Test is_terminal_state for Completed."""
        assert TaskStateMachine.is_terminal_state("Completed") is True

    def test_is_terminal_state_cancelled(self) -> None:
        """Test is_terminal_state for Cancelled."""
        assert TaskStateMachine.is_terminal_state("Cancelled") is True

    def test_is_terminal_state_backlog(self) -> None:
        """Test is_terminal_state for Backlog."""
        assert TaskStateMachine.is_terminal_state("Backlog") is False

    def test_is_terminal_state_in_progress(self) -> None:
        """Test is_terminal_state for In Progress."""
        assert TaskStateMachine.is_terminal_state("In Progress") is False

    def test_is_terminal_state_invalid(self) -> None:
        """Test is_terminal_state with invalid status."""
        assert TaskStateMachine.is_terminal_state("Invalid") is False

    def test_get_initial_state(self) -> None:
        """Test get_initial_state returns Backlog."""
        assert TaskStateMachine.get_initial_state() == "Backlog"

    def test_complete_workflow_sequence(self) -> None:
        """Test a complete workflow sequence from start to finish."""
        # Start
        status = TaskStatus.BACKLOG
        assert TaskStateMachine.is_terminal_state(status.value) is False

        # Claim
        assert TaskStateMachine.can_transition(status, TaskStatus.CLAIMED)
        status = TaskStatus.CLAIMED

        # Start work
        assert TaskStateMachine.can_transition(status, TaskStatus.IN_PROGRESS)
        status = TaskStatus.IN_PROGRESS

        # Submit for review
        assert TaskStateMachine.can_transition(status, TaskStatus.IN_REVIEW)
        status = TaskStatus.IN_REVIEW

        # Complete
        assert TaskStateMachine.can_transition(status, TaskStatus.COMPLETED)
        status = TaskStatus.COMPLETED

        # Terminal state
        assert TaskStateMachine.is_terminal_state(status.value) is True

    def test_workflow_with_revisions(self) -> None:
        """Test workflow where review requests changes."""
        status = TaskStatus.BACKLOG

        # Claim
        status = TaskStatus.CLAIMED

        # Start work
        status = TaskStatus.IN_PROGRESS

        # Submit for review
        status = TaskStatus.IN_REVIEW

        # Request changes (go back to In Progress)
        assert TaskStateMachine.can_transition(status, TaskStatus.IN_PROGRESS)
        status = TaskStatus.IN_PROGRESS

        # Resubmit
        status = TaskStatus.IN_REVIEW

        # Complete
        assert TaskStateMachine.can_transition(status, TaskStatus.COMPLETED)
        status = TaskStatus.COMPLETED

        assert TaskStateMachine.is_terminal_state(status.value) is True

    def test_workflow_cancellation(self) -> None:
        """Test workflow cancellation from different states."""
        # Cancel from Backlog
        assert TaskStateMachine.can_transition(
            TaskStatus.BACKLOG,
            TaskStatus.CANCELLED,
        )

        # Cancel from Claimed
        assert TaskStateMachine.can_transition(
            TaskStatus.CLAIMED,
            TaskStatus.CANCELLED,
        )

        # Cancel from In Progress
        assert TaskStateMachine.can_transition(
            TaskStatus.IN_PROGRESS,
            TaskStatus.CANCELLED,
        )

    def test_workflow_skip_review(self) -> None:
        """Test workflow that skips review step."""
        status = TaskStatus.BACKLOG

        # Claim
        status = TaskStatus.CLAIMED

        # Start work
        status = TaskStatus.IN_PROGRESS

        # Skip directly to Completed
        assert TaskStateMachine.can_transition(status, TaskStatus.COMPLETED)
        status = TaskStatus.COMPLETED

        assert TaskStateMachine.is_terminal_state(status.value) is True
