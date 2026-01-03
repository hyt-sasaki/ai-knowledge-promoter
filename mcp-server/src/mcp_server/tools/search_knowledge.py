"""Search knowledge tool implementation."""

from ..domain.repositories import KnowledgeRepository


def register(mcp, repository: KnowledgeRepository):
    """Register search_knowledge tool to the MCP server.

    Args:
        mcp: The MCP server instance
        repository: Knowledge repository for search
    """

    @mcp.tool
    def search_knowledge(query: str, limit: int = 10) -> list[dict]:
        """Search for knowledge in the system using semantic search.

        Args:
            query: The search query
            limit: Maximum number of results to return (default: 10)

        Returns:
            A list of dicts containing id, title, content, and score

        Raises:
            ValueError: If query is empty or not provided
        """
        if not query or not query.strip():
            raise ValueError("query is required")

        # Search via repository
        result = repository.search(query, limit=limit)

        # Convert to response format
        return [
            {
                "id": item.id,
                "title": item.title,
                "content": item.content,
                "score": item.score,
            }
            for item in result.items
        ]
