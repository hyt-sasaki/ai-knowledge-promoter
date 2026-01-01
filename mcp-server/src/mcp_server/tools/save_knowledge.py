"""Save knowledge tool stub implementation."""

import uuid


def register(mcp):
    """Register save_knowledge tool to the MCP server."""

    @mcp.tool
    def save_knowledge(title: str, content: str, tags: list[str] | None = None) -> dict:
        """
        Save knowledge to the system.

        Args:
            title: The title of the knowledge
            content: The content of the knowledge
            tags: Optional list of tags

        Returns:
            A dict containing status, id, and title

        Raises:
            ValueError: If content is empty or not provided
        """
        if not content or not content.strip():
            raise ValueError("content is required")
        if tags is None:
            tags = []
        # Phase 1: Stub implementation
        return {
            "status": "saved",
            "id": "stub-id-" + str(uuid.uuid4())[:8],
            "title": title,
        }
