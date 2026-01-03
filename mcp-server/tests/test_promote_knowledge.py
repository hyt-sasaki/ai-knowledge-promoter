"""Tests for promote_knowledge tool.

This is Phase 3.1: Test case agreement phase.
All tests use `assert False` pattern to confirm test cases before implementation.
"""

from unittest.mock import MagicMock

import pytest

from mcp_server.domain.models import Knowledge
from mcp_server.tools.promote_knowledge import register


class MockMCP:
    """Mock MCP server for testing."""

    def __init__(self):
        self.tools = {}

    def tool(self, func):
        """Register a tool function."""
        self.tools[func.__name__] = func
        return func


class TestPromoteKnowledge:
    """Tests for promote_knowledge tool.

    Test cases based on verify.md Auto-Test Targets:
    - P1: 昇格成功 (personal/draft → proposed)
    - P2: id空エラー (id="" → "id is required")
    - P2: 存在しないID (id="xxx" → "knowledge not found")
    - P2: 昇格不可状態 (proposed → "only draft can be promoted")
    """

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_mcp = MockMCP()
        self.mock_repository = MagicMock()
        register(self.mock_mcp, self.mock_repository)
        self.promote_knowledge = self.mock_mcp.tools["promote_knowledge"]

    def test_promote_success(self):
        """[P1] Promote knowledge from draft to proposed status.

        WHEN: Valid knowledge ID in draft state
        THEN: Status changes to "proposed"
        """
        # Arrange: Mock repository returns updated knowledge
        self.mock_repository.update_status.return_value = Knowledge(
            id="test-id",
            title="Test Knowledge",
            content="Test content",
            source="personal",
            status="proposed",
        )

        # Act & Assert
        assert False, "TEST CASE AGREEMENT: Implement test logic for promote_success"

    def test_promote_empty_id(self):
        """[P2] Empty id raises ValueError.

        WHEN: id is empty string
        THEN: Raises ValueError with "id is required"
        """
        # Act & Assert
        assert False, "TEST CASE AGREEMENT: Implement test logic for empty id validation"

    def test_promote_not_found(self):
        """[P2] Non-existent knowledge ID raises ValueError.

        WHEN: id does not exist in repository
        THEN: Raises ValueError with "knowledge not found"
        """
        # Arrange: Mock repository returns None
        self.mock_repository.find_by_id.return_value = None

        # Act & Assert
        assert False, "TEST CASE AGREEMENT: Implement test logic for knowledge not found"

    def test_promote_invalid_state(self):
        """[P2] Cannot promote knowledge that is not in draft state.

        WHEN: Knowledge is already in "proposed" or other non-draft state
        THEN: Raises ValueError with "only draft knowledge can be promoted"
        """
        # Arrange: Mock repository returns knowledge in proposed state
        self.mock_repository.find_by_id.return_value = Knowledge(
            id="test-id",
            title="Test Knowledge",
            content="Test content",
            source="personal",
            status="proposed",  # Already proposed
        )

        # Act & Assert
        assert False, "TEST CASE AGREEMENT: Implement test logic for invalid state"
