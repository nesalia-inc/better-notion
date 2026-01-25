"""Tests for RelationParser."""

import pytest

from better_notion._sdk.properties.relation import RelationParser


class TestRelationParserParse:
    """Tests for relation parsing."""

    def test_parse_multiple_relations(self):
        """Test parsing multiple related pages."""
        data = {
            "type": "relation",
            "relation": [
                {"id": "page-123"},
                {"id": "page-456"},
                {"id": "page-789"}
            ]
        }

        result = RelationParser.parse(data)

        assert result == ["page-123", "page-456", "page-789"]

    def test_parse_single_relation(self):
        """Test parsing single related page."""
        data = {
            "type": "relation",
            "relation": [
                {"id": "page-123"}
            ]
        }

        result = RelationParser.parse(data)

        assert result == ["page-123"]

    def test_parse_empty_relation(self):
        """Test parsing empty relation."""
        data = {
            "type": "relation",
            "relation": []
        }

        result = RelationParser.parse(data)

        assert result == []


class TestRelationParserDatabaseId:
    """Tests for database ID extraction."""

    def test_get_database_id(self):
        """Test getting database ID from relation schema."""
        data = {
            "type": "relation",
            "relation": {
                "database_id": "db-abc123",
                "type": "dual_property"
            }
        }

        db_id = RelationParser.get_database_id(data)

        assert db_id == "db-abc123"

    def test_get_database_id_none(self):
        """Test getting database ID when not present."""
        data = {
            "type": "relation",
            "relation": {}
        }

        db_id = RelationParser.get_database_id(data)

        assert db_id is None


class TestRelationParserType:
    """Tests for relation type extraction."""

    def test_get_dual_property_type(self):
        """Test getting dual_property relation type."""
        data = {
            "type": "relation",
            "relation": {
                "database_id": "db-123",
                "type": "dual_property"
            }
        }

        rel_type = RelationParser.get_type(data)

        assert rel_type == "dual_property"

    def test_get_single_property_type(self):
        """Test getting single_property relation type."""
        data = {
            "type": "relation",
            "relation": {
                "database_id": "db-123",
                "type": "single_property"
            }
        }

        rel_type = RelationParser.get_type(data)

        assert rel_type == "single_property"

    def test_get_type_none(self):
        """Test getting type when not present."""
        data = {
            "type": "relation",
            "relation": {}
        }

        rel_type = RelationParser.get_type(data)

        assert rel_type is None


class TestRelationParserCount:
    """Tests for counting related pages."""

    def test_count_multiple(self):
        """Test counting multiple related pages."""
        data = {
            "type": "relation",
            "relation": [
                {"id": "page-1"},
                {"id": "page-2"},
                {"id": "page-3"}
            ]
        }

        count = RelationParser.count(data)

        assert count == 3

    def test_count_one(self):
        """Test counting single related page."""
        data = {
            "type": "relation",
            "relation": [
                {"id": "page-1"}
            ]
        }

        count = RelationParser.count(data)

        assert count == 1

    def test_count_zero(self):
        """Test counting empty relation."""
        data = {
            "type": "relation",
            "relation": []
        }

        count = RelationParser.count(data)

        assert count == 0


class TestRelationParserHasPage:
    """Tests for checking related pages."""

    def test_has_related_page_true(self):
        """Test checking existing related page."""
        data = {
            "type": "relation",
            "relation": [
                {"id": "page-123"},
                {"id": "page-456"}
            ]
        }

        has_page = RelationParser.has_related_page(data, "page-123")

        assert has_page is True

    def test_has_related_page_false(self):
        """Test checking non-existent related page."""
        data = {
            "type": "relation",
            "relation": [
                {"id": "page-123"}
            ]
        }

        has_page = RelationParser.has_related_page(data, "page-999")

        assert has_page is False

    def test_has_related_page_empty(self):
        """Test checking page in empty relation."""
        data = {
            "type": "relation",
            "relation": []
        }

        has_page = RelationParser.has_related_page(data, "page-123")

        assert has_page is False
