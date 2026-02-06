"""Test how to access exception notes."""

import sys


class TestError(Exception):
    """Test error."""


def main():
    """Test exception notes."""
    print(f"Python version: {sys.version}")

    try:
        raise TestError("Something went wrong")
    except TestError as e:
        e.add_note("Note 1")
        e.add_note("Note 2")

        print(f"\nstr(e): {str(e)}")
        print(f"repr(e): {repr(e)}")

        # Check if notes are accessible
        if hasattr(e, "__notes__"):
            print(f"e.__notes__: {e.__notes__}")
            print(f"Notes in str(e): {'Note 1' in str(e)}")

        # Try to format the exception with notes
        import traceback
        print("\nTraceback with notes:")
        traceback.print_exc()


if __name__ == "__main__":
    main()
