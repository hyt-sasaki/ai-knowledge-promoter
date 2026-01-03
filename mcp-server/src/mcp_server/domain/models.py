"""Domain models for knowledge management."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Knowledge:
    """Knowledge domain model.

    Represents a piece of knowledge stored in the system.

    Attributes:
        id: Unique identifier for the knowledge
        title: Title of the knowledge
        content: Main content of the knowledge
        tags: List of tags for categorization
        user_id: Developer identifier (fixed "anonymous" in Phase 2)
        source: Origin of knowledge ("personal" or "team")
        status: Lifecycle status ("draft", "proposed", or "promoted")
        path: GitHub file path (empty string for personal knowledge)
        created_at: Creation timestamp (ISO 8601)
        updated_at: Last update timestamp (ISO 8601)
        score: Search relevance score (only for search results)
    """

    id: str
    title: str
    content: str
    tags: list[str] = field(default_factory=list)
    user_id: str = "anonymous"
    source: str = "personal"
    status: str = "draft"
    path: str = ""
    created_at: datetime | None = None
    updated_at: datetime | None = None
    score: float | None = None


@dataclass
class SearchResult:
    """Search result container.

    Attributes:
        items: List of matching Knowledge objects
        total: Total number of matches
    """

    items: list[Knowledge]
    total: int
