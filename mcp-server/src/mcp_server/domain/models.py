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
        github_path: GitHub file path (team/promoted only)
        pr_url: Promotion PR URL (personal/proposed only)
        promoted_from_id: Original knowledge ID (team/promoted only)
        created_at: Creation timestamp (ISO 8601)
        updated_at: Last update timestamp (ISO 8601)
        score: Search relevance score (only for search results)

    Valid state combinations:
        - personal/draft: github_path="", pr_url="", promoted_from_id=""
        - personal/proposed: github_path="", pr_url=URL, promoted_from_id=""
        - team/promoted: github_path=path, pr_url="", promoted_from_id=ID
        - team/promoted (GitHub direct): github_path=path, promoted_from_id=""
    """

    id: str
    title: str
    content: str
    tags: list[str] = field(default_factory=list)
    user_id: str = "anonymous"

    # Lifecycle management
    source: str = "personal"
    status: str = "draft"

    # GitHub integration
    github_path: str = ""
    pr_url: str = ""
    promoted_from_id: str = ""

    # Timestamps
    created_at: datetime | None = None
    updated_at: datetime | None = None

    # Search-only
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
