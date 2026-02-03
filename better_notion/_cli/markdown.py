"""Markdown to Notion block converter.

This module provides functionality to parse Markdown files and convert them
into Notion blocks for page creation.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from better_notion._api.properties import RichText


class MarkdownParser:
    """Parse Markdown and convert to Notion blocks."""

    # Markdown patterns
    HEADING_1 = re.compile(r"^#\s+(.+)$")
    HEADING_2 = re.compile(r"^##\s+(.+)$")
    HEADING_3 = re.compile(r"^###\s+(.+)$")
    BULLET = re.compile(r"^[\-\*]\s+(.+)$")
    NUMBERED = re.compile(r"^\d+\.\s+(.+)$")
    QUOTE = re.compile(r"^>\s*(.*)$")
    CODE_BLOCK = re.compile(r"^```(\w*)\n(.*?)\n```$", re.DOTALL)
    INLINE_CODE = re.compile(r"`([^`]+)`")
    DIVIDER = re.compile(r"^(---|\*\*\*)$")
    TODO_CHECKED = re.compile(r"^\[x\]\s*(.+)$")
    TODO_UNCHECKED = re.compile(r"^\[\s\]\s*(.+)$")

    def __init__(self, content: str) -> None:
        """Initialize parser with markdown content.

        Args:
            content: Markdown file content
        """
        self.content = content
        self.lines = content.split("\n")
        self.blocks: list[dict[str, Any]] = []
        self.in_code_block = False
        self.code_lang = ""
        self.code_lines: list[str] = []

    def parse(self) -> list[dict[str, Any]]:
        """Parse markdown and return list of Notion block data.

        Returns:
            List of block dictionaries compatible with Notion API
        """
        i = 0
        while i < len(self.lines):
            line = self.lines[i]

            # Skip empty lines
            if not line.strip():
                i += 1
                continue

            # Code blocks (multi-line)
            if line.startswith("```"):
                i = self._parse_code_block(i)
                continue

            # Headings
            if h1_match := self.HEADING_1.match(line):
                self.blocks.append(self._create_heading(h1_match.group(1), 1))

            elif h2_match := self.HEADING_2.match(line):
                self.blocks.append(self._create_heading(h2_match.group(1), 2))

            elif h3_match := self.HEADING_3.match(line):
                self.blocks.append(self._create_heading(h3_match.group(1), 3))

            # Lists
            elif bullet_match := self.BULLET.match(line):
                self.blocks.append(self._create_bullet(bullet_match.group(1)))

            elif numbered_match := self.NUMBERED.match(line):
                self.blocks.append(self._create_numbered(numbered_match.group(1)))

            # Todos
            elif todo_checked := self.TODO_CHECKED.match(line):
                self.blocks.append(self._create_todo(todo_checked.group(1), checked=True))

            elif todo_unchecked := self.TODO_UNCHECKED.match(line):
                self.blocks.append(self._create_todo(todo_unchecked.group(1), checked=False))

            # Quote
            elif quote_match := self.QUOTE.match(line):
                self.blocks.append(self._create_quote(quote_match.group(1)))

            # Divider
            elif self.DIVIDER.match(line):
                self.blocks.append(self._create_divider())

            # Paragraph (default)
            else:
                # Check if next lines are part of the same paragraph
                paragraph_lines = [line]
                j = i + 1
                while j < len(self.lines) and self._is_paragraph_continuation(self.lines[j]):
                    paragraph_lines.append(self.lines[j].strip())
                    j += 1

                paragraph_text = " ".join(paragraph_lines)
                if paragraph_text.strip():  # Only add if non-empty
                    self.blocks.append(self._create_paragraph(paragraph_text))

                i = j - 1  # Adjust for outer increment

            i += 1

        return self.blocks

    def _is_paragraph_continuation(self, line: str) -> bool:
        """Check if line continues the current paragraph.

        Args:
            line: Line to check

        Returns:
            True if line is a continuation
        """
        stripped = line.strip()
        # Empty lines break paragraphs
        if not stripped:
            return False
        # Any block syntax breaks paragraphs
        if (stripped.startswith("#") or
            stripped.startswith("-") or
            stripped.startswith("*") or
            re.match(r"^\d+\.", stripped) or
            stripped.startswith(">") or
            stripped.startswith("---") or
            stripped.startswith("[") or
            stripped.startswith("```")):
            return False
        return True

    def _parse_code_block(self, start_idx: int) -> int:
        """Parse a multi-line code block.

        Args:
            start_idx: Starting line index

        Returns:
            Index of line after code block
        """
        # Extract language from opening ```lang
        first_line = self.lines[start_idx]
        lang = first_line[3:].strip() or "text"

        # Find closing ```
        code_lines = []
        i = start_idx + 1
        while i < len(self.lines) and not self.lines[i].startswith("```"):
            code_lines.append(self.lines[i])
            i += 1

        code = "\n".join(code_lines)
        self.blocks.append(self._create_code(code, lang))
        return i  # Return index of closing ```

    def _create_rich_text(self, content: str) -> list[dict[str, Any]]:
        """Create rich text array from markdown inline formatting.

        Args:
            content: Text content with markdown formatting

        Returns:
            Rich text array with Notion annotations
        """
        if not content:
            return []

        # Patterns for inline formatting (order matters for nested formatting)
        patterns = [
            # Bold: **text** or __text__
            (r'\*\*(.+?)\*\*', 'bold'),
            (r'__(.+?)__', 'bold'),
            # Italic: *text* or _text_ (but not mid-word)
            (r'(?<!\w)\*(?!\*)(.+?)(?<!\*)\*(?!\w)', 'italic'),
            (r'(?<!\w)_(?!_)(.+?)(?<!_)_(?!\w)', 'italic'),
            # Strikethrough: ~~text~~
            (r'~~(.+?)~~', 'strikethrough'),
            # Inline code: `text`
            (r'`(.+?)`', 'code'),
            # Links: [text](url)
            (r'\[(.+?)\]\((.+?)\)', 'link'),
        ]

        rich_text = []
        remaining = content
        last_end = 0

        while remaining:
            # Find the first matching pattern
            earliest_match = None
            earliest_pos = -1
            matched_pattern = None

            for pattern, style in patterns:
                match = re.search(pattern, remaining)
                if match and (earliest_pos == -1 or match.start() < earliest_pos):
                    earliest_match = match
                    earliest_pos = match.start()
                    matched_pattern = (pattern, style)

            if earliest_match:
                # Add text before the match
                if earliest_pos > 0:
                    rich_text.append({"type": "text", "text": {"content": remaining[:earliest_pos]}})

                # Process the match based on style
                style = matched_pattern[1]

                if style == 'link':
                    # Link format: [text](url)
                    link_text = earliest_match.group(1)
                    link_url = earliest_match.group(2)
                    rich_text.append({
                        "type": "text",
                        "text": {"content": link_text, "link": {"url": link_url}}
                    })
                else:
                    # Text with annotation
                    text_content = earliest_match.group(1)
                    rich_text_obj = {"type": "text", "text": {"content": text_content}}

                    # Add annotation
                    annotations = {"bold": False, "italic": False, "strikethrough": False, "code": False, "underline": False}
                    annotations[style] = True
                    rich_text_obj["annotations"] = annotations

                    rich_text.append(rich_text_obj)

                # Move past this match
                remaining = remaining[earliest_match.end():]
                last_end = earliest_match.end()
            else:
                # No more matches, add remaining text
                if remaining:
                    rich_text.append({"type": "text", "text": {"content": remaining}})
                break

        return rich_text if rich_text else [{"type": "text", "text": {"content": content}}]

    def _create_paragraph(self, text: str) -> dict[str, Any]:
        """Create a paragraph block.

        Args:
            text: Paragraph text

        Returns:
            Paragraph block data
        """
        return {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": self._create_rich_text(text)
            }
        }

    def _create_heading(self, text: str, level: int) -> dict[str, Any]:
        """Create a heading block.

        Args:
            text: Heading text
            level: Heading level (1-3)

        Returns:
            Heading block data
        """
        heading_type = f"heading_{level}"
        return {
            "object": "block",
            "type": heading_type,
            heading_type: {
                "rich_text": self._create_rich_text(text)
            }
        }

    def _create_bullet(self, text: str) -> dict[str, Any]:
        """Create a bullet list item block.

        Args:
            text: Bullet text

        Returns:
            Bullet block data
        """
        return {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": self._create_rich_text(text)
            }
        }

    def _create_numbered(self, text: str) -> dict[str, Any]:
        """Create a numbered list item block.

        Args:
            text: Numbered item text

        Returns:
            Numbered block data
        """
        return {
            "object": "block",
            "type": "numbered_list_item",
            "numbered_list_item": {
                "rich_text": self._create_rich_text(text)
            }
        }

    def _create_todo(self, text: str, checked: bool) -> dict[str, Any]:
        """Create a todo block.

        Args:
            text: Todo text
            checked: Checked state

        Returns:
            Todo block data
        """
        return {
            "object": "block",
            "type": "to_do",
            "to_do": {
                "rich_text": self._create_rich_text(text),
                "checked": checked
            }
        }

    def _create_quote(self, text: str) -> dict[str, Any]:
        """Create a quote block.

        Args:
            text: Quote text

        Returns:
            Quote block data
        """
        return {
            "object": "block",
            "type": "quote",
            "quote": {
                "rich_text": self._create_rich_text(text)
            }
        }

    def _create_code(self, code: str, language: str = "text") -> dict[str, Any]:
        """Create a code block.

        Args:
            code: Code content
            language: Programming language

        Returns:
            Code block data
        """
        return {
            "object": "block",
            "type": "code",
            "code": {
                "rich_text": [{"type": "text", "text": {"content": code}}],
                "language": language
            }
        }

    def _create_divider(self) -> dict[str, Any]:
        """Create a divider block.

        Returns:
            Divider block data
        """
        return {
            "object": "block",
            "type": "divider",
            "divider": {}
        }

    def get_title(self) -> str:
        """Extract page title from markdown.

        Returns:
            First H1 text or empty string
        """
        for line in self.lines:
            if match := self.HEADING_1.match(line):
                return match.group(1)
        return ""


def parse_markdown_file(file_path: str | Path) -> tuple[str, list[dict[str, Any]]]:
    """Parse a markdown file and return title and blocks.

    Args:
        file_path: Path to markdown file

    Returns:
        Tuple of (title, blocks_list)

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file is empty or invalid
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Markdown file not found: {file_path}")

    content = path.read_text(encoding="utf-8")

    if not content.strip():
        raise ValueError(f"Markdown file is empty: {file_path}")

    parser = MarkdownParser(content)
    blocks = parser.parse()
    title = parser.get_title() or path.stem

    return title, blocks
