"""Tests for VectorSearchArchivedKnowledgeRepository.

Phase 3: Tests for archive repository implementation.
"""

import os
from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest
from google.api_core.exceptions import NotFound

from mcp_server.domain.models import ArchivedKnowledge
from mcp_server.infrastructure.archive_repository import (
    VectorSearchArchivedKnowledgeRepository,
)


class TestVectorSearchArchivedKnowledgeRepositoryInit:
    """Tests for repository initialization."""

    @patch(
        "mcp_server.infrastructure.archive_repository.vectorsearch_v1beta"
        ".DataObjectServiceClient"
    )
    def test_init_with_explicit_project_id(self, mock_data):
        """Repository initializes with explicit project_id."""
        repo = VectorSearchArchivedKnowledgeRepository(project_id="test-project")
        assert repo.project_id == "test-project"
        assert repo.location == "us-central1"
        assert repo.collection_id == "archived-knowledge"


class TestVectorSearchArchivedKnowledgeRepository:
    """Tests for VectorSearchArchivedKnowledgeRepository.

    Test selection constraints applied:
    - C1 coverage: Minimum cases for branch coverage
    - Equivalence partitioning: Consolidated redundant cases
    - Priority: P1 normal cases only (repository is infrastructure layer)
    """

    def setup_method(self):
        """Set up test fixtures."""
        with patch.dict(os.environ, {"GCP_PROJECT_ID": "test-project"}):
            self.repo = VectorSearchArchivedKnowledgeRepository()
            self.repo._data_object_client = MagicMock()

    # P1: 正常系 - 保存
    def test_save_archived_knowledge(self):
        """Save archived knowledge to collection.

        WHEN: ArchivedKnowledge オブジェクトを save
        THEN: コレクションに保存され、同じオブジェクトが返る
        """
        now = datetime.now(UTC)
        archived = ArchivedKnowledge(
            id="original-id",
            title="Archived Title",
            content="Archived content",
            tags=["tag1"],
            user_id="user-123",
            promoted_to_id="promoted-id",
            archived_at=now,
            original_created_at=now,
        )

        # Mock the create_data_object response
        mock_response = MagicMock()
        mock_response.data_object_id = "original-id"
        self.repo._data_object_client.create_data_object.return_value = mock_response

        result = self.repo.save(archived)

        assert result.id == "original-id"
        assert result.title == "Archived Title"
        self.repo._data_object_client.create_data_object.assert_called_once()

    # P1: 正常系 - 取得
    def test_get_archived_knowledge(self):
        """Get archived knowledge by ID.

        WHEN: 存在する ID で get
        THEN: ArchivedKnowledge が返る
        """
        now = datetime.now(UTC)

        # Mock the get_data_object response
        mock_response = MagicMock()
        mock_response.data = {
            "title": "Archived Title",
            "content": "Archived content",
            "tags": ["tag1"],
            "user_id": "user-123",
            "promoted_to_id": "promoted-id",
            "archived_at": now.isoformat(),
            "original_created_at": now.isoformat(),
        }
        self.repo._data_object_client.get_data_object.return_value = mock_response

        result = self.repo.get("original-id")

        assert result is not None
        assert result.id == "original-id"
        assert result.title == "Archived Title"
        self.repo._data_object_client.get_data_object.assert_called_once()

    # P2: 境界 - 存在しないID
    def test_get_not_found(self):
        """Get returns None for non-existent ID.

        WHEN: 存在しない ID で get
        THEN: None が返る
        """
        self.repo._data_object_client.get_data_object.side_effect = NotFound(
            "Not found"
        )

        result = self.repo.get("nonexistent-id")

        assert result is None
