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
            path: GitHub file path

        Returns:
            Knowledge if found, None otherwise
        """
        ...

    def find_by_pr_url(self, url: str) -> Knowledge | None:
        """Find knowledge by PR URL.

        Args:
            url: Pull request URL

        Returns:
            Knowledge if found, None otherwise
        """
        ...

    def update_status(
        self, id: str, status: str, *, pr_url: str = ""
    ) -> Knowledge | None:
        """Update knowledge status.

        Args:
            id: Knowledge identifier
            status: New status ("draft", "proposed", "promoted")
            pr_url: PR URL (optional, for proposed status)

        Returns:
            Updated knowledge if found, None otherwise
        """
        ...


class ArchivedKnowledgeRepository(Protocol):
    """Repository interface for archived knowledge.

    Used for storing knowledge that has been promoted and archived.
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
        """Get archived knowledge by ID.

        Args:
            id: Archived knowledge identifier (original knowledge ID)

        Returns:
            ArchivedKnowledge if found, None otherwise
        """
        ...
