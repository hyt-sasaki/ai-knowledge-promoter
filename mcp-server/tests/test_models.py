"""Tests for domain models."""

from datetime import UTC, datetime

from mcp_server.domain.models import Knowledge, SearchResult


class TestKnowledge:
    """Tests for Knowledge dataclass."""

    def test_init_with_required_fields(self):
        """Knowledge can be initialized with required fields only."""
        knowledge = Knowledge(
            id="test-id",
            title="Test Title",
            content="Test content",
        )

        assert knowledge.id == "test-id"
        assert knowledge.title == "Test Title"
        assert knowledge.content == "Test content"
        assert knowledge.tags == []
        assert knowledge.user_id == "anonymous"
        assert knowledge.source == "personal"
        assert knowledge.status == "draft"
        assert knowledge.path == ""
        assert knowledge.created_at is None
        assert knowledge.updated_at is None
        assert knowledge.score is None

    def test_init_with_all_fields(self):
        """Knowledge can be initialized with all fields."""
        now = datetime.now(UTC)
        knowledge = Knowledge(
            id="test-id",
            title="Test Title",
            content="Test content",
            tags=["tag1", "tag2"],
            user_id="user-123",
            source="team",
            status="proposed",
            path="/path/to/file.md",
            created_at=now,
            updated_at=now,
            score=0.95,
        )

        assert knowledge.id == "test-id"
        assert knowledge.tags == ["tag1", "tag2"]
        assert knowledge.user_id == "user-123"
        assert knowledge.source == "team"
        assert knowledge.status == "proposed"
        assert knowledge.path == "/path/to/file.md"
        assert knowledge.created_at == now
        assert knowledge.updated_at == now
        assert knowledge.score == 0.95


class TestSearchResult:
    """Tests for SearchResult dataclass."""

    def test_init_empty(self):
        """SearchResult can be initialized with empty items."""
        result = SearchResult(items=[], total=0)

        assert result.items == []
        assert result.total == 0

    def test_init_with_items(self):
        """SearchResult can be initialized with Knowledge items."""
        items = [
            Knowledge(id="1", title="First", content="Content 1", score=0.9),
            Knowledge(id="2", title="Second", content="Content 2", score=0.8),
        ]
        result = SearchResult(items=items, total=2)

        assert len(result.items) == 2
        assert result.total == 2
        assert result.items[0].title == "First"
        assert result.items[1].title == "Second"
