"""Tests for VectorSearchKnowledgeRepository error handling."""

import os
from unittest.mock import MagicMock, patch

import pytest
from google.api_core.exceptions import GoogleAPICallError, NotFound

from mcp_server.domain.models import Knowledge
from mcp_server.infrastructure.vector_search import VectorSearchKnowledgeRepository


class TestVectorSearchKnowledgeRepositoryInit:
    """Tests for repository initialization."""

    @patch(
        "mcp_server.infrastructure.vector_search.vectorsearch_v1beta"
        ".DataObjectServiceClient"
    )
    @patch(
        "mcp_server.infrastructure.vector_search.vectorsearch_v1beta"
        ".DataObjectSearchServiceClient"
    )
    def test_init_with_explicit_project_id(self, mock_search, mock_data):
        """Repository initializes with explicit project_id."""
        repo = VectorSearchKnowledgeRepository(project_id="test-project")
        assert repo.project_id == "test-project"
        assert repo.location == "us-central1"
        assert repo.collection_id == "knowledge"

    @patch(
        "mcp_server.infrastructure.vector_search.vectorsearch_v1beta"
        ".DataObjectServiceClient"
    )
    @patch(
        "mcp_server.infrastructure.vector_search.vectorsearch_v1beta"
        ".DataObjectSearchServiceClient"
    )
    def test_init_with_env_var(self, mock_search, mock_data):
        """Repository initializes with GCP_PROJECT_ID env var."""
        with patch.dict(os.environ, {"GCP_PROJECT_ID": "env-project"}):
            repo = VectorSearchKnowledgeRepository()
            assert repo.project_id == "env-project"

    def test_init_raises_without_project_id(self):
        """Repository raises ValueError without project_id."""
        with patch.dict(
            os.environ, {"GCP_PROJECT_ID": "", "GOOGLE_CLOUD_PROJECT": ""}, clear=False
        ):
            # Clear the env vars
            env = os.environ.copy()
            env.pop("GCP_PROJECT_ID", None)
            env.pop("GOOGLE_CLOUD_PROJECT", None)

            with patch.dict(os.environ, env, clear=True), pytest.raises(
                ValueError, match="project_id must be provided"
            ):
                VectorSearchKnowledgeRepository()


class TestVectorSearchKnowledgeRepositoryErrorHandling:
    """Tests for repository error handling."""

    def setup_method(self):
        """Set up test fixtures."""
        with patch.dict(os.environ, {"GCP_PROJECT_ID": "test-project"}):
            self.repo = VectorSearchKnowledgeRepository()
            self.repo._data_object_client = MagicMock()
            self.repo._search_client = MagicMock()

    def test_get_returns_none_on_not_found(self):
        """get() returns None when knowledge not found."""
        self.repo._data_object_client.get_data_object.side_effect = NotFound(
            "Not found"
        )

        result = self.repo.get("nonexistent-id")

        assert result is None

    def test_get_returns_none_on_api_error(self):
        """get() returns None on API error."""
        self.repo._data_object_client.get_data_object.side_effect = GoogleAPICallError(
            "API error"
        )

        result = self.repo.get("some-id")

        assert result is None

    def test_delete_returns_false_on_not_found(self):
        """delete() returns False when knowledge not found."""
        self.repo._data_object_client.delete_data_object.side_effect = NotFound(
            "Not found"
        )

        result = self.repo.delete("nonexistent-id")

        assert result is False

    def test_delete_returns_false_on_api_error(self):
        """delete() returns False on API error."""
        self.repo._data_object_client.delete_data_object.side_effect = (
            GoogleAPICallError("API error")
        )

        result = self.repo.delete("some-id")

        assert result is False

    def test_save_raises_on_api_error(self):
        """save() raises RepositoryError on API error."""
        self.repo._data_object_client.create_data_object.side_effect = (
            GoogleAPICallError("API error")
        )

        knowledge = Knowledge(id="", title="Test", content="Content")

        with pytest.raises(Exception):  # Should raise RepositoryError
            self.repo.save(knowledge)

    def test_search_raises_on_api_error(self):
        """search() raises RepositoryError on API error."""
        self.repo._search_client.search_data_objects.side_effect = GoogleAPICallError(
            "API error"
        )

        with pytest.raises(Exception):  # Should raise RepositoryError
            self.repo.search("test query")
