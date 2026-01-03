"""Tests for search_knowledge tool."""

from unittest.mock import MagicMock

import pytest

from mcp_server.domain.models import Knowledge, SearchResult
from mcp_server.tools.search_knowledge import register


class MockMCP:
    """Mock MCP server for testing."""

    def __init__(self):
        self.tools = {}

    def tool(self, func):
        """Register a tool function."""
        self.tools[func.__name__] = func
        return func


class TestSearchKnowledge:
    """Tests for search_knowledge tool."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_mcp = MockMCP()
        self.mock_repository = MagicMock()
        register(self.mock_mcp, self.mock_repository)
        self.search_knowledge = self.mock_mcp.tools["search_knowledge"]

    def test_search_returns_results(self):
        """Search returns results from repository."""
        self.mock_repository.search.return_value = SearchResult(
            items=[
                Knowledge(
                    id="1",
                    title="First Result",
                    content="Content 1",
                    score=0.95,
                ),
                Knowledge(
                    id="2",
                    title="Second Result",
                    content="Content 2",
                    score=0.85,
                ),
            ],
            total=2,
        )

        result = self.search_knowledge(query="test query", limit=10)

        assert len(result) == 2
        assert result[0]["id"] == "1"
        assert result[0]["title"] == "First Result"
        assert result[0]["content"] == "Content 1"
        assert result[0]["score"] == 0.95
        assert result[1]["id"] == "2"

        # Verify repository was called with correct arguments
        self.mock_repository.search.assert_called_once_with("test query", limit=10)

    def test_search_returns_empty_list(self):
        """Search returns empty list when no results."""
        self.mock_repository.search.return_value = SearchResult(items=[], total=0)

        result = self.search_knowledge(query="no match", limit=10)

        assert result == []

    def test_search_empty_query_raises_error(self):
        """Empty query raises ValueError."""
        with pytest.raises(ValueError, match="query is required"):
            self.search_knowledge(query="")

    def test_search_whitespace_query_raises_error(self):
        """Whitespace-only query raises ValueError."""
        with pytest.raises(ValueError, match="query is required"):
            self.search_knowledge(query="   ")

    def test_search_uses_default_limit(self):
        """Search uses default limit of 10."""
        self.mock_repository.search.return_value = SearchResult(items=[], total=0)

        self.search_knowledge(query="test")

        self.mock_repository.search.assert_called_once_with("test", limit=10)

    def test_search_with_custom_limit(self):
        """Search respects custom limit."""
        self.mock_repository.search.return_value = SearchResult(items=[], total=0)

        self.search_knowledge(query="test", limit=5)

        self.mock_repository.search.assert_called_once_with("test", limit=5)
