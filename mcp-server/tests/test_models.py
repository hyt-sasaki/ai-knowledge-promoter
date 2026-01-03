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
        # New fields for promotion workflow
        assert knowledge.github_path == ""
        assert knowledge.pr_url == ""
        assert knowledge.promoted_from_id == ""
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
            status="promoted",
            github_path="docs/knowledge/test.md",
            pr_url="",
            promoted_from_id="original-id-123",
            created_at=now,
            updated_at=now,
            score=0.95,
        )

        assert knowledge.id == "test-id"
        assert knowledge.tags == ["tag1", "tag2"]
        assert knowledge.user_id == "user-123"
        assert knowledge.source == "team"
        assert knowledge.status == "promoted"
        assert knowledge.github_path == "docs/knowledge/test.md"
        assert knowledge.pr_url == ""
        assert knowledge.promoted_from_id == "original-id-123"
        assert knowledge.created_at == now
        assert knowledge.updated_at == now
        assert knowledge.score == 0.95

    def test_personal_draft_state(self):
        """Personal draft knowledge has correct default fields."""
        knowledge = Knowledge(
            id="draft-id",
            title="Draft",
            content="Draft content",
        )

        assert knowledge.source == "personal"
        assert knowledge.status == "draft"
        assert knowledge.github_path == ""
        assert knowledge.pr_url == ""
        assert knowledge.promoted_from_id == ""

    def test_personal_proposed_state(self):
        """Personal proposed knowledge has pr_url set."""
        knowledge = Knowledge(
            id="proposed-id",
            title="Proposed",
            content="Proposed content",
            source="personal",
            status="proposed",
            pr_url="https://github.com/org/repo/pull/123",
        )

        assert knowledge.source == "personal"
        assert knowledge.status == "proposed"
        assert knowledge.github_path == ""
        assert knowledge.pr_url == "https://github.com/org/repo/pull/123"
        assert knowledge.promoted_from_id == ""

    def test_team_promoted_from_personal_state(self):
        """Team promoted knowledge (from personal) has correct fields."""
        knowledge = Knowledge(
            id="promoted-id",
            title="Promoted",
            content="Promoted content",
            source="team",
            status="promoted",
            github_path="docs/knowledge/promoted.md",
            promoted_from_id="original-personal-id",
        )

        assert knowledge.source == "team"
        assert knowledge.status == "promoted"
        assert knowledge.github_path == "docs/knowledge/promoted.md"
        assert knowledge.pr_url == ""
        assert knowledge.promoted_from_id == "original-personal-id"

    def test_team_promoted_from_github_state(self):
        """Team promoted knowledge (from GitHub direct) has empty promoted_from_id."""
        knowledge = Knowledge(
            id="github-direct-id",
            title="GitHub Direct",
            content="Created directly on GitHub",
            source="team",
            status="promoted",
            github_path="docs/knowledge/direct.md",
            promoted_from_id="",
        )

        assert knowledge.source == "team"
        assert knowledge.status == "promoted"
        assert knowledge.github_path == "docs/knowledge/direct.md"
        assert knowledge.pr_url == ""
        assert knowledge.promoted_from_id == ""


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
