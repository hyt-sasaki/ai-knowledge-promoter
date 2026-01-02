"""Tests for save_knowledge tool."""

from unittest.mock import MagicMock

import pytest

from mcp_server.domain.models import Knowledge
from mcp_server.tools.save_knowledge import register


class MockMCP:
    """Mock MCP server for testing."""

    def __init__(self):
        self.tools = {}

    def tool(self, func):
        """Register a tool function."""
        self.tools[func.__name__] = func
        return func


class TestSaveKnowledge:
    """Tests for save_knowledge tool."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_mcp = MockMCP()
        self.mock_repository = MagicMock()
        register(self.mock_mcp, self.mock_repository)
        self.save_knowledge = self.mock_mcp.tools["save_knowledge"]

    def test_save_with_title_and_content(self):
        """Save knowledge with title and content."""
        self.mock_repository.save.return_value = Knowledge(
            id="generated-id",
            title="Test Title",
            content="Test content",
        )

        result = self.save_knowledge(
            title="Test Title",
            content="Test content",
            tags=["tag1"],
        )

        assert result["status"] == "saved"
        assert result["id"] == "generated-id"
        assert result["title"] == "Test Title"

        # Verify repository was called
        self.mock_repository.save.assert_called_once()
        saved_knowledge = self.mock_repository.save.call_args[0][0]
        assert saved_knowledge.title == "Test Title"
        assert saved_knowledge.content == "Test content"
        assert saved_knowledge.tags == ["tag1"]

    def test_save_auto_generates_title_from_content(self):
        """Title is auto-generated from content when not provided."""
        content = "This is a long content that should be truncated"
        expected_title = content[:30] + "..."

        self.mock_repository.save.return_value = Knowledge(
            id="generated-id",
            title=expected_title,
            content=content,
        )

        result = self.save_knowledge(
            title=None,
            content=content,
        )

        assert result["status"] == "saved"

        # Verify repository received auto-generated title
        saved_knowledge = self.mock_repository.save.call_args[0][0]
        assert saved_knowledge.title == expected_title

    def test_save_auto_generates_title_short_content(self):
        """Title is auto-generated without truncation for short content."""
        self.mock_repository.save.return_value = Knowledge(
            id="generated-id",
            title="Short",
            content="Short",
        )

        result = self.save_knowledge(
            title=None,
            content="Short",
        )

        assert result["status"] == "saved"

        saved_knowledge = self.mock_repository.save.call_args[0][0]
        assert saved_knowledge.title == "Short"

    def test_save_empty_content_raises_error(self):
        """Empty content raises ValueError."""
        with pytest.raises(ValueError, match="content is required"):
            self.save_knowledge(title="Title", content="")

    def test_save_whitespace_content_raises_error(self):
        """Whitespace-only content raises ValueError."""
        with pytest.raises(ValueError, match="content is required"):
            self.save_knowledge(title="Title", content="   ")

    def test_save_none_tags_defaults_to_empty_list(self):
        """None tags defaults to empty list."""
        self.mock_repository.save.return_value = Knowledge(
            id="generated-id",
            title="Title",
            content="Content",
            tags=[],
        )

        self.save_knowledge(title="Title", content="Content", tags=None)

        saved_knowledge = self.mock_repository.save.call_args[0][0]
        assert saved_knowledge.tags == []
