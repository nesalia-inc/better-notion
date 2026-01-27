"""Property builders for Notion entities."""

from better_notion._api.properties.base import Property
from better_notion._api.properties.rich_text import RichText, Text, create_rich_text_array
from better_notion._api.properties.title import Title
from better_notion._api.properties.select import Select, MultiSelect
from better_notion._api.properties.checkbox import Checkbox
from better_notion._api.properties.date import Date, CreatedTime, LastEditedTime
from better_notion._api.properties.number import Number
from better_notion._api.properties.url import URL
from better_notion._api.properties.email import Email
from better_notion._api.properties.phone import Phone

__all__ = [
    "Property",
    "RichText",
    "Text",
    "create_rich_text_array",
    "Title",
    "Select",
    "MultiSelect",
    "Checkbox",
    "Date",
    "CreatedTime",
    "LastEditedTime",
    "Number",
    "URL",
    "Email",
    "Phone",
]
