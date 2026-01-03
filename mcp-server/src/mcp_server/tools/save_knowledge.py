"""Save knowledge tool implementation."""

from ..domain.models import Knowledge
from ..domain.repositories import KnowledgeRepository


def register(mcp, repository: KnowledgeRepository):
    """Register save_knowledge tool to the MCP server.

    Args:
        mcp: The MCP server instance
        repository: Knowledge repository for persistence
    """

    @mcp.tool
    def save_knowledge(
        title: str | None = None, content: str = "", tags: list[str] | None = None
    ) -> dict:
        """Save knowledge to the system.

        Args:
            title: Title of the knowledge (optional, auto-generated if not provided)
            content: The content of the knowledge (required)
            tags: Optional list of tags

        Returns:
            A dict containing status, id, and title

        Raises:
            ValueError: If content is empty or not provided
        """
        if not content or not content.strip():
            raise ValueError("content is required")

        # Auto-generate title from content if not provided
        if not title or not title.strip():
            title = content[:30].strip()
            if len(content) > 30:
                title += "..."

        if tags is None:
            tags = []

        # Create knowledge model
        knowledge = Knowledge(
            id="",  # Will be auto-generated
            title=title,
            content=content,
            tags=tags,
        )

        # Save via repository
        saved = repository.save(knowledge)

        return {
            "status": "saved",
            "id": saved.id,
            "title": saved.title,
        }
