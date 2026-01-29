"""Validation helpers for CLI commands.

This module provides reusable validation functions for CLI parameters.
"""


class ValidationError(Exception):
    """Custom exception for validation errors."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class Validators:
    """Reusable validation functions for CLI parameters."""

    @staticmethod
    def positive_int(value: int, name: str = "value") -> None:
        """
        Validate that a value is a positive integer.

        Args:
            value: The value to validate
            name: Parameter name for error messages

        Raises:
            ValidationError: If value is not positive
        """
        if not isinstance(value, int):
            raise ValidationError(f"{name} must be an integer (got: {type(value).__name__})")
        if value <= 0:
            raise ValidationError(f"{name} must be positive (greater than 0, got: {value})")

    @staticmethod
    def non_negative_int(value: int, name: str = "value") -> None:
        """
        Validate that a value is a non-negative integer.

        Args:
            value: The value to validate
            name: Parameter name for error messages

        Raises:
            ValidationError: If value is negative
        """
        if not isinstance(value, int):
            raise ValidationError(f"{name} must be an integer (got: {type(value).__name__})")
        if value < 0:
            raise ValidationError(f"{name} must be non-negative (0 or greater, got: {value})")

    @staticmethod
    def non_negative_float(value: float, name: str = "value") -> None:
        """
        Validate that a value is a non-negative float.

        Args:
            value: The value to validate
            name: Parameter name for error messages

        Raises:
            ValidationError: If value is negative
        """
        if not isinstance(value, (int, float)):
            raise ValidationError(f"{name} must be a number (got: {type(value).__name__})")
        if value < 0:
            raise ValidationError(f"{name} must be non-negative (0 or greater, got: {value})")

    @staticmethod
    def enum(value: str, name: str, allowed: list, case_sensitive: bool = False) -> None:
        """
        Validate that a value is in the allowed list.

        Args:
            value: The value to validate
            name: Parameter name for error messages
            allowed: List of allowed values
            case_sensitive: Whether comparison should be case-sensitive

        Raises:
            ValidationError: If value is not in allowed list
        """
        if not case_sensitive:
            value_lower = value.lower()
            allowed_lower = [a.lower() for a in allowed]
            if value_lower not in allowed_lower:
                raise ValidationError(
                    f"{name} must be one of {allowed} (got: {value})"
                )
        else:
            if value not in allowed:
                raise ValidationError(
                    f"{name} must be one of {allowed} (got: {value})"
                )

    @staticmethod
    def range_int(value: int, name: str, min_val: int, max_val: int) -> None:
        """
        Validate that a value is within a specified range.

        Args:
            value: The value to validate
            name: Parameter name for error messages
            min_val: Minimum allowed value (inclusive)
            max_val: Maximum allowed value (inclusive)

        Raises:
            ValidationError: If value is outside the range
        """
        if not isinstance(value, int):
            raise ValidationError(f"{name} must be an integer (got: {type(value).__name__})")
        if value < min_val or value > max_val:
            raise ValidationError(
                f"{name} must be between {min_val} and {max_val} (got: {value})"
            )

    @staticmethod
    def required(value: Any, name: str) -> None:
        """
        Validate that a value is not None or empty.

        Args:
            value: The value to validate
            name: Parameter name for error messages

        Raises:
            ValidationError: If value is None or empty
        """
        if value is None:
            raise ValidationError(f"{name} is required")
        if isinstance(value, str) and not value.strip():
            raise ValidationError(f"{name} cannot be empty")
