"""Test property builders."""

from better_notion._api.properties import Title, Text, Number, Date

# Test Title
title = Title("Test Page")
title_dict = title.to_dict()
print(f"Title dict: {title_dict}")

# Test Text
text = Text("Description", "Some text")
text_dict = text.to_dict()
print(f"Text dict: {text_dict}")
print(f"Text dict keys: {text_dict.keys()}")

# Test Number
number = Number("Count", 42)
number_dict = number.to_dict()
print(f"Number dict: {number_dict}")

# Test Date
date = Date("Due Date", "2025-01-01")
date_dict = date.to_dict()
print(f"Date dict: {date_dict}")
