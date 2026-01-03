"""Repository interfaces for knowledge management.

This module defines the Protocol (interface) for knowledge repositories,
following the Dependency Inversion Principle (DIP).
"""

from typing import Protocol

from .models import ArchivedKnowledge, Knowledge, SearchResult


class KnowledgeRepository(Protocol):
    """Repository interface for knowledge persistence and search.

    Tools layer depends on this interface, not concrete implementations.
    Concrete implementations are provided in the infrastructure layer.
    """

    def save(self, knowledge: Knowledge) -> Knowledge:
        """Save knowledge and return the saved instance with ID.

        - If id is empty, creates a new knowledge (auto-generates ID)
        - If id is provided, updates existing knowledge
        - created_at and updated_at are auto-assigned by implementation

        Args:
            knowledge: The knowledge to save

        Returns:
            The saved knowledge with ID and timestamps populated
        """
        ...

    def search(
        self,
        query: str,
        *,
        limit: int = 20,
    ) -> SearchResult:
        """Search knowledge using semantic search.

        Args:
            query: Search query text
            limit: Maximum number of results (default: 20)

        Returns:
            SearchResult containing matching items
        """
        ...

    def get(self, id: str) -> Knowledge | None:
        """Get knowledge by ID.

        Args:
            id: Knowledge identifier

        Returns:
            Knowledge if found, None otherwise
        """
        ...

    def delete(self, id: str) -> bool:
        """Delete knowledge by ID.

        Args:
            id: Knowledge identifier

        Returns:
            True if deleted, False if not found
        """
        ...

    def find_by_github_path(self, path: str) -> Knowledge | None:
        """Find knowledge by GitHub file path.

        Args:
            path: GitHub file path (e.g., "docs/knowledge/example.md")

        Returns:
            Knowledge if found, None otherwise
        """
        ...

    def find_by_pr_url(self, url: str) -> Knowledge | None:
        """Find knowledge by promotion PR URL.

        Args:
            url: GitHub PR URL (e.g., "https://github.com/org/repo/pull/123")

        Returns:
            Knowledge if found, None otherwise
        """
        ...

    def update_status(
        self,
        id: str,
        status: str,
        *,
        pr_url: str | None = None,
        github_path: str | None = None,
    ) -> Knowledge:
        """Update knowledge status and optional fields.

        Args:
            id: Knowledge identifier
            status: New status ("draft", "proposed", or "promoted")
            pr_url: Optional PR URL to set (for proposed status)
            github_path: Optional GitHub path to set (for promoted status)

        Returns:
            Updated knowledge

        Raises:
            ValueError: If knowledge not found or invalid status transition
        """
        ...


class ArchivedKnowledgeRepository(Protocol):
    """Repository interface for archived knowledge.

    Stores knowledge that has been archived after promotion.
    """

    def save(self, archived: ArchivedKnowledge) -> ArchivedKnowledge:
        """Save archived knowledge.

        Args:
            archived: The archived knowledge to save

        Returns:
            The saved archived knowledge
        """
        ...

    def get(self, id: str) -> ArchivedKnowledge | None:
        """Get archived knowledge by original ID.

        Args:
            id: Original knowledge identifier

        Returns:
            ArchivedKnowledge if found, None otherwise
        """
        ...
