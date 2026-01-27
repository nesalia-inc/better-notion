"""Rich text and text property builders."""

from __future__ import annotations

from typing import Any

from better_notion._api.properties.base import Property


class RichText(Property):
    """Builder for rich text properties."""

    def __init__(
        self,
        name: str,
        content: str,
        *,
        bold: bool = False,
        italic: bool = False,
        strikethrough: bool = False,
        underline: bool = False,
        code: bool = False,
        link: str | None = None,
    ) -> None:
        """Initialize a rich text property.

        Args:
            name: The property name.
            content: The text content.
            bold: Whether text is bold.
            italic: Whether text is italic.
            strikethrough: Whether text is strikethrough.
            underline: Whether text is underlined.
            code: Whether text is code.
            link: Optional URL link.
        """
        super().__init__(name)
        self._content = content
        self._bold = bold
        self._italic = italic
        self._strikethrough = strikethrough
        self._underline = underline
        self._code = code
        self._link = link

    def to_dict(self) -> dict[str, Any]:
        """Convert to Notion API format."""
        text_obj = {"content": self._content}
        if self._link:
            text_obj["link"] = {"url": self._link}

        annotations: dict[str, Any] = {}
        if self._bold:
            annotations["bold"] = True
        if self._italic:
            annotations["italic"] = True
        if self._strikethrough:
            annotations["strikethrough"] = True
        if self._underline:
            annotations["underline"] = True
        if self._code:
            annotations["code"] = True

        rich_text_obj: dict[str, Any] = {
            "type": "text",
            "text": text_obj,
        }

        if annotations:
            rich_text_obj["annotations"] = annotations

        return rich_text_obj


class Text(Property):
    """Builder for text properties."""

    def __init__(self, name: str, content: str) -> None:
        """Initialize a text property.

        Args:
            name: The property name.
            content: The text content.
        """
        super().__init__(name)
        self._content = content

    def to_dict(self) -> dict[str, Any]:
        """Convert to Notion API format."""
        return {
            "type": "text",
            "text": [
                {
                    "type": "text",
                    "text": {"content": self._content}
                }
            ]
        }


def create_rich_text_array(content: str, **kwargs: Any) -> list[dict[str, Any]]:
    """Create a rich text array for block content.

    This is a convenience function for creating rich text arrays
    used in block content (paragraphs, headings, etc.).

    Args:
        content: The text content.
        **kwargs: Optional formatting options (bold, italic, etc.)

    Returns:
        A list with a single rich text object in Notion API format.

    Example:
        >>> create_rich_text_array("Hello, world!")
        [{'type': 'text', 'text': {'content': 'Hello, world!'}}]
        >>> create_rich_text_array("Bold text", bold=True)
        [{'type': 'text', 'text': {'content': 'Bold text'}, 'annotations': {'bold': True}}]
    """
    rich_text = RichText(name="", content=content, **kwargs)
    return [rich_text.to_dict()]
