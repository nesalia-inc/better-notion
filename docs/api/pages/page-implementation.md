# Page Implementation Guide

Technical implementation guide for building the Page system in Better Notion SDK.

## Architecture Overview

### Class Hierarchy

```
NotionObject
└── Page
    ├── PropertiesManager
    ├── ContentManager (blocks)
    └── Property classes
        ├── TitleProperty
        ├── StatusProperty
        ├── DateProperty
        ├── SelectProperty
        ├── MultiSelectProperty
        ├── etc.
```

## Core Page Class

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, List, Union
from uuid import UUID
from enum import Enum

class PageParentType(str, Enum):
    """Types of page parents."""
    DATABASE_ID = "database_id"
    PAGE_ID = "page_id"
    WORKSPACE = "workspace"
    BLOCK_ID = "block_id"

@dataclass
class PageParent:
    """Page parent information."""
    type: PageParentType
    database_id: Optional[UUID] = None
    page_id: Optional[UUID] = None
    workspace: bool = False
    block_id: Optional[UUID] = None

    @classmethod
    def from_dict(cls, data: dict) -> "PageParent":
        """Parse parent from API response."""
        parent_type = PageParentType(data.get("type"))

        kwargs = {"type": parent_type}

        if parent_type == PageParentType.DATABASE_ID:
            kwargs["database_id"] = UUID(data.get("database_id"))
        elif parent_type == PageParentType.PAGE_ID:
            kwargs["page_id"] = UUID(data.get("page_id"))
        elif parent_type == PageParentType.WORKSPACE:
            kwargs["workspace"] = True
        elif parent_type == PageParentType.BLOCK_ID:
            kwargs["block_id"] = UUID(data.get("block_id"))

        return cls(**kwargs)

    def to_dict(self) -> dict:
        """Convert to API-compatible dict."""
        if self.type == PageParentType.DATABASE_ID:
            return {"type": self.type.value, "database_id": str(self.database_id)}
        elif self.type == PageParentType.PAGE_ID:
            return {"type": self.type.value, "page_id": str(self.page_id)}
        elif self.type == PageParentType.WORKSPACE:
            return {"type": self.type.value, "workspace": True}
        elif self.type == PageParentType.BLOCK_ID:
            return {"type": self.type.value, "block_id": str(self.block_id)}

@dataclass
class Icon:
    """Page icon (emoji or file)."""
    type: str  # "emoji" or "external" or "file"
    emoji: Optional[str] = None
    file_url: Optional[str] = None
    file_expiry: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: Optional[dict]) -> Optional["Icon"]:
        """Parse icon from API response."""
        if not data:
            return None

        icon_type = data.get("type")

        if icon_type == "emoji":
            return cls(type=icon_type, emoji=data.get("emoji"))
        elif icon_type in ["external", "file"]:
            file_data = data.get(icon_type, {})
            expiry = file_data.get("expiry_time")
            if expiry:
                expiry = datetime.fromisoformat(expiry.replace("Z", "+00:00"))
            return cls(type=icon_type, file_url=file_data.get("url"), file_expiry=expiry)

        return None

    def to_dict(self) -> dict:
        """Convert to API-compatible dict."""
        if self.type == "emoji":
            return {"type": "emoji", "emoji": self.emoji}
        elif self.type == "external":
            return {"type": "external", "external": {"url": self.file_url}}
        elif self.type == "file_upload":
            return {"type": "file_upload", "file_upload": {"id": self.file_url}}

@dataclass
class Page:
    """Notion page object."""
    object: str = "page"
    id: UUID = None
    created_time: Optional[datetime] = None
    last_edited_time: Optional[datetime] = None
    created_by: Optional[Any] = None  # PartialUser
    last_edited_by: Optional[Any] = None  # PartialUser
    archived: bool = False
    in_trash: bool = False
    cover: Optional[str] = None  # Cover URL
    icon: Optional[Icon] = None
    parent: Optional[PageParent] = None
    url: str = ""
    public_url: Optional[str] = None

    # Properties (parsed)
    _properties: Dict[str, "PropertyValue"] = field(default_factory=dict, repr=False)

    # Client reference
    _client: Any = field(default=None, init=False, repr=False)

    # Lazy-loaded content
    _blocks: Optional[List["Block"]] = field(default=None, init=False, repr=False)

    @classmethod
    def from_dict(cls, data: dict, client: Any = None) -> "Page":
        """Parse page from API response."""
        instance = cls()

        # Basic fields
        instance.object = data.get("object")
        instance.id = UUID(data.get("id"))
        instance.created_time = _parse_datetime(data.get("created_time"))
        instance.last_edited_time = _parse_datetime(data.get("last_edited_time"))
        instance.archived = data.get("archived", False)
        instance.in_trash = data.get("in_trash", False)
        instance.url = data.get("url", "")
        instance.public_url = data.get("public_url")

        # Parent
        if "parent" in data:
            instance.parent = PageParent.from_dict(data["parent"])

        # Icon
        instance.icon = Icon.from_dict(data.get("icon"))

        # Cover
        cover_data = data.get("cover")
        if cover_data:
            if cover_data.get("type") == "external":
                instance.cover = cover_data["external"]["url"]

        # Parse properties
        properties_data = data.get("properties", {})
        instance._properties = PropertyParser.parse_properties(properties_data)

        # Store client reference
        instance._client = client

        return instance

    def to_dict(self, include_properties: bool = True) -> dict:
        """Convert page to API-compatible dict."""
        data = {
            "object": self.object,
            "id": str(self.id),
            "archived": self.archived,
        }

        if self.parent:
            data["parent"] = self.parent.to_dict()

        if self.icon:
            data["icon"] = self.icon.to_dict()

        if self.cover:
            data["cover"] = {"type": "external", "external": {"url": self.cover}}

        if include_properties:
            data["properties"] = {
                name: prop.to_dict()
                for name, prop in self._properties.items()
            }

        return data

    # Convenience properties

    @property
    def title(self) -> str:
        """Get page title."""
        title_prop = self._properties.get("title")
        if title_prop and hasattr(title_prop, "plain_text"):
            return title_prop.plain_text
        return ""

    @property
    def properties(self) -> "PropertiesManager":
        """Get properties manager."""
        return PropertiesManager(self._properties, self._client, self.id)

    @property
    def content(self) -> "ContentManager":
        """Get content manager for blocks."""
        return ContentManager(self.id, self._client, self._blocks)

    # CRUD operations

    async def refresh(self) -> None:
        """Refresh page data from API."""
        if not self._client:
            raise RuntimeError("Cannot refresh without client reference")

        updated = await self._client.pages.get(str(self.id))

        # Update fields
        self._properties = updated._properties
        self.last_edited_time = updated.last_edited_time
        self.last_edited_by = updated.last_edited_by
        self.archived = updated.archived
        self.in_trash = updated.in_trash

        # Clear cached blocks
        self._blocks = None

    async def save(self) -> "Page":
        """Save changes to page."""
        if not self._client:
            raise RuntimeError("Cannot save without client reference")

        # Prepare update data
        update_data = {"archived": self.archived}

        if self.icon:
            update_data["icon"] = self.icon.to_dict()

        if self.cover:
            update_data["cover"] = {"type": "external", "external": {"url": self.cover}}

        # Send update
        response = await self._client.pages.update(
            page_id=str(self.id),
            **update_data
        )

        return Page.from_dict(response, self._client)

    async def archive(self) -> "Page":
        """Archive the page."""
        self.archived = True
        return await self.save()

    async def unarchive(self) -> "Page":
        """Unarchive the page."""
        self.archived = False
        return await self.save()

    async def delete(self) -> None:
        """Delete the page permanently."""
        if not self._client:
            raise RuntimeError("Cannot delete without client reference")

        await self._client.blocks.delete(str(self.id))
```

## Properties Manager

```python
@dataclass
class PropertiesManager:
    """Manager for page properties."""
    _properties: Dict[str, "PropertyValue"]
    _client: Any
    _page_id: UUID

    def get(self, property_name: str) -> Optional["PropertyValue"]:
        """Get a property by name."""
        return self._properties.get(property_name)

    def get_by_id(self, property_id: str) -> Optional["PropertyValue"]:
        """Get a property by ID."""
        for prop in self._properties.values():
            if prop.id == property_id:
                return prop
        return None

    def all(self) -> Dict[str, "PropertyValue"]:
        """Get all properties."""
        return self._properties.copy()

    async def update(self, **properties) -> "Page":
        """Update properties."""
        if not self._client:
            raise RuntimeError("Cannot update without client reference")

        # Build properties dict for API
        properties_dict = {}
        for name, value in properties.items():
            if isinstance(value, PropertyValue):
                properties_dict[name] = value.to_dict()
            else:
                # Assume it's a dict already in API format
                properties_dict[name] = value

        # Send update
        response = await self._client.pages.update(
            page_id=str(self._page_id),
            properties=properties_dict
        )

        return Page.from_dict(response, self._client)

    async def set_title(self, title: str) -> "Page":
        """Set page title."""
        return await self.update(
            title={
                "title": [
                    {
                        "type": "text",
                        "text": {"content": title}
                    }
                ]
            }
        )

    async def set_status(self, status: str) -> "Page":
        """Set status property."""
        return await self.update(
            status={"status": {"name": status}}
        )

    async def set_date(self, property_name: str, start: str, end: Optional[str] = None) -> "Page":
        """Set a date property."""
        date_value = {"start": start}
        if end:
            date_value["end"] = end

        return await self.update(
            **{property_name: {"date": date_value}}
        )
```

## Property Parser

```python
class PropertyParser:
    """Parse page properties from API responses."""

    @staticmethod
    def parse_properties(properties_data: dict) -> Dict[str, "PropertyValue"]:
        """Parse all properties."""
        properties = {}

        for name, prop_data in properties_data.items():
            prop = PropertyParser.parse_property(prop_data)
            properties[name] = prop

        return properties

    @staticmethod
    def parse_property(data: dict) -> "PropertyValue":
        """Parse a single property."""
        prop_type = data.get("type")
        prop_id = data.get("id")

        if prop_type == "title":
            return TitleProperty.from_dict(data, prop_id)
        elif prop_type == "status":
            return StatusProperty.from_dict(data, prop_id)
        elif prop_type == "select":
            return SelectProperty.from_dict(data, prop_id)
        elif prop_type == "multi_select":
            return MultiSelectProperty.from_dict(data, prop_id)
        elif prop_type == "date":
            return DateProperty.from_dict(data, prop_id)
        elif prop_type == "checkbox":
            return CheckboxProperty.from_dict(data, prop_id)
        elif prop_type == "number":
            return NumberProperty.from_dict(data, prop_id)
        elif prop_type == "email":
            return EmailProperty.from_dict(data, prop_id)
        elif prop_type == "phone_number":
            return PhoneNumberProperty.from_dict(data, prop_id)
        elif prop_type == "url":
            return URLProperty.from_dict(data, prop_id)
        elif prop_type == "rich_text":
            return RichTextProperty.from_dict(data, prop_id)
        elif prop_type == "people":
            return PeopleProperty.from_dict(data, prop_id)
        elif prop_type == "files":
            return FilesProperty.from_dict(data, prop_id)
        elif prop_type == "relation":
            return RelationProperty.from_dict(data, prop_id)
        elif prop_type == "formula":
            return FormulaProperty.from_dict(data, prop_id)
        elif prop_type == "rollup":
            return RollupProperty.from_dict(data, prop_id)
        elif prop_type == "created_by":
            return CreatedByProperty.from_dict(data, prop_id)
        elif prop_type == "created_time":
            return CreatedTimeProperty.from_dict(data, prop_id)
        elif prop_type == "last_edited_by":
            return LastEditedByProperty.from_dict(data, prop_id)
        elif prop_type == "last_edited_time":
            return LastEditedTimeProperty.from_dict(data, prop_id)
        elif prop_type == "unique_id":
            return UniqueIDProperty.from_dict(data, prop_id)
        elif prop_type == "verification":
            return VerificationProperty.from_dict(data, prop_id)
        else:
            return UnsupportedProperty(prop_id, prop_type, data.get(prop_type))
```

## Property Base Class

```python
from abc import ABC, abstractmethod

class PropertyValue(ABC):
    """Base class for all property values."""

    def __init__(self, prop_id: str, prop_type: str):
        self.id = prop_id
        self.type = prop_type

    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict, prop_id: str) -> "PropertyValue":
        """Parse property from API response."""
        pass

    @abstractmethod
    def to_dict(self) -> dict:
        """Convert property to API format."""
        pass

    @property
    def is_readonly(self) -> bool:
        """Whether this property is read-only."""
        return self.type in READONLY_TYPES

READONLY_TYPES = {
    "created_by",
    "created_time",
    "last_edited_by",
    "last_edited_time",
    "formula",
    "rollup",
    "unique_id",
    "verification"
}
```

## Concrete Property Classes

### Title Property

```python
class TitleProperty(PropertyValue):
    """Title property."""

    def __init__(self, prop_id: str, title: List[RichTextObject]):
        super().__init__(prop_id, "title")
        self.title = title

    @classmethod
    def from_dict(cls, data: dict, prop_id: str) -> "TitleProperty":
        """Parse from API response."""
        title_data = data.get("title", [])
        title = RichTextParser.parse_array(title_data)
        return cls(prop_id, title)

    def to_dict(self) -> dict:
        """Convert to API format."""
        return {
            "title": [rt.to_dict() for rt in self.title]
        }

    @property
    def plain_text(self) -> str:
        """Get plain text title."""
        return "".join(rt.plain_text for rt in self.title)

    def __str__(self) -> str:
        return self.plain_text
```

### Status Property

```python
@dataclass
class StatusOption:
    """Status option."""
    id: str
    name: str
    color: str

class StatusProperty(PropertyValue):
    """Status property."""

    def __init__(self, prop_id: str, status: Optional[StatusOption]):
        super().__init__(prop_id, "status")
        self.status = status

    @classmethod
    def from_dict(cls, data: dict, prop_id: str) -> "StatusProperty":
        """Parse from API response."""
        status_data = data.get("status")
        if status_data:
            status = StatusOption(
                id=status_data.get("id"),
                name=status_data.get("name"),
                color=status_data.get("color")
            )
        else:
            status = None
        return cls(prop_id, status)

    def to_dict(self) -> dict:
        """Convert to API format."""
        if self.status:
            return {
                "status": {"name": self.status.name}
            }
        return {"status": None}

    def __str__(self) -> str:
        return self.status.name if self.status else ""
```

### Select Property

```python
class SelectProperty(PropertyValue):
    """Select property."""

    def __init__(self, prop_id: str, select: Optional[StatusOption]):
        super().__init__(prop_id, "select")
        self.select = select

    @classmethod
    def from_dict(cls, data: dict, prop_id: str) -> "SelectProperty":
        """Parse from API response."""
        select_data = data.get("select")
        if select_data:
            select = StatusOption(
                id=select_data.get("id"),
                name=select_data.get("name"),
                color=select_data.get("color")
            )
        else:
            select = None
        return cls(prop_id, select)

    def to_dict(self) -> dict:
        """Convert to API format."""
        if self.select:
            return {
                "select": {"name": self.select.name}
            }
        return {"select": None}
```

### Multi-Select Property

```python
class MultiSelectProperty(PropertyValue):
    """Multi-select property."""

    def __init__(self, prop_id: str, multi_select: List[StatusOption]):
        super().__init__(prop_id, "multi_select")
        self.multi_select = multi_select

    @classmethod
    def from_dict(cls, data: dict, prop_id: str) -> "MultiSelectProperty":
        """Parse from API response."""
        options_data = data.get("multi_select", [])
        options = [
            StatusOption(
                id=opt.get("id"),
                name=opt.get("name"),
                color=opt.get("color")
            )
            for opt in options_data
        ]
        return cls(prop_id, options)

    def to_dict(self) -> dict:
        """Convert to API format."""
        return {
            "multi_select": [
                {"name": opt.name}
                for opt in self.multi_select
            ]
        }

    def add_option(self, name: str) -> None:
        """Add an option by name."""
        # Create a new option (will be added to schema on save)
        self.multi_select.append(
            StatusOption(id="", name=name, color="default")
        )

    def remove_option(self, name: str) -> None:
        """Remove an option by name."""
        self.multi_select = [opt for opt in self.multi_select if opt.name != name]

    def has_option(self, name: str) -> bool:
        """Check if option exists."""
        return any(opt.name == name for opt in self.multi_select)
```

### Date Property

```python
@dataclass
class DateValue:
    """Date value."""
    start: Union[datetime, date]
    end: Optional[Union[datetime, date]] = None
    time_zone: Optional[str] = None

class DateProperty(PropertyValue):
    """Date property."""

    def __init__(self, prop_id: str, date: Optional[DateValue]):
        super().__init__(prop_id, "date")
        self.date = date

    @classmethod
    def from_dict(cls, data: dict, prop_id: str) -> "DateProperty":
        """Parse from API response."""
        date_data = data.get("date")
        if date_data:
            start = _parse_datetime(date_data.get("start"))
            end = _parse_datetime(date_data.get("end"))
            time_zone = date_data.get("time_zone")
            date = DateValue(start=start, end=end, time_zone=time_zone)
        else:
            date = None
        return cls(prop_id, date)

    def to_dict(self) -> dict:
        """Convert to API format."""
        if self.date:
            date_dict = {"start": _format_datetime(self.date.start)}
            if self.date.end:
                date_dict["end"] = _format_datetime(self.date.end)
            if self.date.time_zone:
                date_dict["time_zone"] = self.date.time_zone
            return {"date": date_dict}
        return {"date": None}

def _parse_datetime(value: Optional[str]) -> Optional[Union[datetime, date]]:
    """Parse ISO 8601 datetime string."""
    if not value:
        return None

    # Try parsing as datetime first
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        pass

    # Try parsing as date
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None

def _format_datetime(value: Union[datetime, date]) -> str:
    """Format datetime/date to ISO 8601 string."""
    if isinstance(value, datetime):
        return value.isoformat(timespec="milliseconds").replace("+00:00", "Z")
    elif isinstance(value, date):
        return value.isoformat()
    return str(value)
```

### Checkbox Property

```python
class CheckboxProperty(PropertyValue):
    """Checkbox property."""

    def __init__(self, prop_id: str, checkbox: bool):
        super().__init__(prop_id, "checkbox")
        self.value = checkbox

    @classmethod
    def from_dict(cls, data: dict, prop_id: str) -> "CheckboxProperty":
        """Parse from API response."""
        return cls(prop_id, data.get("checkbox", False))

    def to_dict(self) -> dict:
        """Convert to API format."""
        return {"checkbox": self.value}

    def toggle(self) -> bool:
        """Toggle checkbox."""
        self.value = not self.value
        return self.value

    @property
    def is_checked(self) -> bool:
        """Whether checkbox is checked."""
        return self.value
```

### Number Property

```python
class NumberProperty(PropertyValue):
    """Number property."""

    def __init__(self, prop_id: str, number: Optional[float]):
        super().__init__(prop_id, "number")
        self.value = number

    @classmethod
    def from_dict(cls, data: dict, prop_id: str) -> "NumberProperty":
        """Parse from API response."""
        return cls(prop_id, data.get("number"))

    def to_dict(self) -> dict:
        """Convert to API format."""
        return {"number": self.value}
```

## Content Manager

```python
@dataclass
class ContentManager:
    """Manager for page content (blocks)."""
    _page_id: UUID
    _client: Any
    _cached_blocks: Optional[List[Block]]

    async def get_blocks(self, force_refresh: bool = False) -> List[Block]:
        """Get all blocks in the page."""
        if force_refresh or self._cached_blocks is None:
            if not self._client:
                raise RuntimeError("Cannot fetch blocks without client")

            all_blocks = []
            has_more = True
            cursor = None

            while has_more:
                response = await self._client.blocks.children.list(
                    block_id=str(self._page_id),
                    start_cursor=cursor
                )
                blocks = [
                    Block.from_dict(block_data, self._client)
                    for block_data in response.get("results", [])
                ]
                all_blocks.extend(blocks)
                has_more = response.get("has_more", False)
                cursor = response.get("next_cursor")

            self._cached_blocks = all_blocks

        return self._cached_blocks

    async def append(self, *blocks: Block) -> List[Block]:
        """Append blocks to page."""
        if not self._client:
            raise RuntimeError("Cannot append blocks without client")

        block_data = [block.to_dict() for block in blocks]

        response = await self._client.blocks.children.append(
            block_id=str(self._page_id),
            children=block_data
        )

        new_blocks = [
            Block.from_dict(block_data, self._client)
            for block_data in response.get("results", [])
        ]

        # Clear cache
        self._cached_blocks = None

        return new_blocks

    async def append_paragraph(self, text: str) -> Block:
        """Append a paragraph block."""
        paragraph = BlockFactory.create_paragraph(text)
        result = await self.append(paragraph)
        return result[0] if result else None

    async def append_heading(self, text: str, level: int = 1) -> Block:
        """Append a heading block."""
        heading = BlockFactory.create_heading(text, level)
        result = await self.append(heading)
        return result[0] if result else None
```

## Usage Examples

### Working with Pages

```python
# Get a page
page = await client.pages.get(page_id)

# Access title
print(page.title)

# Get properties
status_prop = page.properties.get("Status")
print(status_prop.status.name)  # "In Progress"

# Update properties
await page.properties.set_status("Done")
await page.properties.set_date("Due date", "2023-12-31")

# Get page content
blocks = await page.content.get_blocks()
for block in blocks:
    print(block.type, block.plain_text)

# Add content to page
await page.content.append_paragraph("New paragraph")

# Archive page
await page.archive()
```

### Creating Pages

```python
# Create in database
page = await client.pages.create(
    parent={"type": "database_id", "database_id": database_id},
    properties={
        "Name": {
            "title": [{"type": "text", "text": {"content": "New Page"}}]
        },
        "Status": {"status": {"name": "Not Started"}}
    }
)

# Create as child page
child_page = await client.pages.create(
    parent={"type": "page_id", "page_id": parent_page_id},
    properties={
        "title": [{"type": "text", "text": {"content": "Child Page"}}]
    }
)
```

### Property Helpers

```python
# Using property managers
page.properties.update(
    status={"status": {"name": "Done"}},
    priority={"select": {"name": "High"}}
)

# Get specific property
date_prop = page.properties.get("Due date")
if date_prop and date_prop.date:
    print(f"Due: {date_prop.date.start}")

# Multi-select operations
tags = page.properties.get("Tags")
if tags:
    tags.add_option("Python")
    tags.remove_option("JavaScript")
    await page.properties.update(Tags=tags)
```

## Implementation Checklist

### Core Classes
- [ ] `Page` class with all fields
- [ ] `PageParent` class
- [ ] `Icon` class
- [ ] `PropertiesManager` class
- [ ] `ContentManager` class
- [ ] `PropertyParser` class

### Property Classes
- [ ] `PropertyValue` base class
- [ ] `TitleProperty`
- [ ] `StatusProperty`
- [ ] `SelectProperty`
- [ ] `MultiSelectProperty`
- [ ] `DateProperty`
- [ ] `CheckboxProperty`
- [ ] `NumberProperty`
- [ ] `EmailProperty`
- [ ] `PhoneNumberProperty`
- [ ] `URLProperty`
- [ ] `RichTextProperty`
- [ ] `PeopleProperty`
- [ ] `FilesProperty`
- [ ] `RelationProperty`
- [ ] `FormulaProperty`
- [ ] `RollupProperty`
- [ ] `CreatedByProperty`
- [ ] `CreatedTimeProperty`
- [ ] `LastEditedByProperty`
- [ ] `LastEditedTimeProperty`
- [ ] `UniqueIDProperty`
- [ ] `VerificationProperty`
- [ ] `UnsupportedProperty`

### Helpers
- [ ] Date/time parsing utilities
- [ ] Rich text parser integration
- [ ] Block manager integration
- [ ] Property validation

### Testing
- [ ] Unit tests for each property type
- [ ] Integration tests with API
- [ ] Tests for page CRUD operations
- [ ] Tests for property updates
- [ ] Tests for content management

---

**Related Documentation:**
- [Pages Overview](./pages-overview.md) - Page concepts
- [Page Properties](./page-properties.md) - Property reference
- [Rich Text Objects](../rich-text-objects.md) - Text in properties
- [Blocks](../block/blocks-overview.md) - Page content
