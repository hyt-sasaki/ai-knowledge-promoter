"""Tests for promote_knowledge tool.

Phase 3: Assert False skeleton - test cases to be agreed upon before implementation.
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

    Test selection constraints applied:
    - C1 coverage: Minimum cases for branch coverage
    - Equivalence partitioning: Consolidated redundant cases
    - Priority: P1 normal case + P2 boundary cases (max 3)
    """

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_mcp = MockMCP()
        self.mock_repository = MagicMock()
        register(self.mock_mcp, self.mock_repository)
        self.promote_knowledge = self.mock_mcp.tools["promote_knowledge"]

    # P1: 正常系 - コアパス
    def test_promote_success(self):
        """Promote knowledge from draft to proposed status.

        WHEN: personal/draft の knowledge ID を指定
        THEN: status が "proposed" に更新される
        """
        # Arrange: draft 状態の knowledge をモック
        self.mock_repository.get.return_value = Knowledge(
            id="draft-id",
            title="Draft Title",
            content="Draft content",
            source="personal",
            status="draft",
        )
        self.mock_repository.update_status.return_value = Knowledge(
            id="draft-id",
            title="Draft Title",
            content="Draft content",
            source="personal",
            status="proposed",
        )

        # Act
        result = self.promote_knowledge(id="draft-id")

        # Assert
        assert result["status"] == "proposed"
        assert result["id"] == "draft-id"
        self.mock_repository.get.assert_called_once_with("draft-id")
        self.mock_repository.update_status.assert_called_once_with(
            "draft-id", "proposed"
        )

    # P2: バリデーション - id空
    def test_promote_empty_id(self):
        """Empty id raises ValueError.

        WHEN: id が空文字列
        THEN: ValueError("id is required") が発生
        """
        with pytest.raises(ValueError, match="id is required"):
            self.promote_knowledge(id="")

    def test_promote_whitespace_id(self):
        """Whitespace-only id raises ValueError."""
        with pytest.raises(ValueError, match="id is required"):
            self.promote_knowledge(id="   ")

    # P2: エラーハンドリング - 存在しないID
    def test_promote_not_found(self):
        """Non-existent id raises error.

        WHEN: 存在しない ID を指定
        THEN: ValueError("knowledge not found") が発生
        """
        self.mock_repository.get.return_value = None

        with pytest.raises(ValueError, match="knowledge not found"):
            self.promote_knowledge(id="non-existent-id")

        self.mock_repository.get.assert_called_once_with("non-existent-id")

    # P2: ビジネスルール - 昇格不可状態
    def test_promote_invalid_state(self):
        """Non-draft knowledge cannot be promoted.

        WHEN: status が "proposed" の knowledge を昇格しようとする
        THEN: ValueError("only draft knowledge can be promoted") が発生
        """
        self.mock_repository.get.return_value = Knowledge(
            id="proposed-id",
            title="Proposed Title",
            content="Proposed content",
            source="personal",
            status="proposed",
        )

        with pytest.raises(ValueError, match="only draft knowledge can be promoted"):
            self.promote_knowledge(id="proposed-id")

        self.mock_repository.get.assert_called_once_with("proposed-id")
        self.mock_repository.update_status.assert_not_called()
