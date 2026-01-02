"""Tests for delete_knowledge tool."""

from unittest.mock import MagicMock

import pytest

from mcp_server.tools.delete_knowledge import register


class MockMCP:
    """Mock MCP server for testing."""

    def __init__(self):
        self.tools = {}

    def tool(self, func):
        """Register a tool function."""
        self.tools[func.__name__] = func
        return func


class TestDeleteKnowledge:
    """Tests for delete_knowledge tool."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_mcp = MockMCP()
        self.mock_repository = MagicMock()
        register(self.mock_mcp, self.mock_repository)
        self.delete_knowledge = self.mock_mcp.tools["delete_knowledge"]

    def test_delete_success(self):
        """Delete returns success when repository deletes."""
        self.mock_repository.delete.return_value = True

        result = self.delete_knowledge(id="test-id")

        assert result["status"] == "deleted"
        assert result["id"] == "test-id"
        self.mock_repository.delete.assert_called_once_with("test-id")

    def test_delete_not_found(self):
        """Delete returns not_found when ID doesn't exist."""
        self.mock_repository.delete.return_value = False

        result = self.delete_knowledge(id="nonexistent-id")

        assert result["status"] == "not_found"
        assert result["id"] == "nonexistent-id"
        self.mock_repository.delete.assert_called_once_with("nonexistent-id")

    def test_delete_empty_id_raises_error(self):
        """Empty ID raises ValueError."""
        with pytest.raises(ValueError, match="id is required"):
            self.delete_knowledge(id="")

    def test_delete_whitespace_id_raises_error(self):
        """Whitespace-only ID raises ValueError."""
        with pytest.raises(ValueError, match="id is required"):
            self.delete_knowledge(id="   ")
