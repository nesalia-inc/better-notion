"""Test Relation property."""

from better_notion._api.properties import Relation

# Test Relation property with name parameter
relation = Relation("Domain", ["page_123"])
print(f"Name: {relation._name}")
print(f"Page IDs: {relation._page_ids}")

relation_dict = relation.to_dict()
print(f"Relation dict: {relation_dict}")
print(f"Keys: {relation_dict.keys()}")

# Check each key
for key, value in relation_dict.items():
    print(f"  {key}: {value}")
