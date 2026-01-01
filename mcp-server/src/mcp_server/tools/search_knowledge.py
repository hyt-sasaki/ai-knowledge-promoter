"""Search knowledge tool stub implementation."""


def register(mcp):
    """Register search_knowledge tool to the MCP server."""

    @mcp.tool
    def search_knowledge(query: str, limit: int = 10) -> list[dict]:
        """
        Search for knowledge in the system.

        Args:
            query: The search query
            limit: Maximum number of results to return (default: 10)

        Returns:
            A list of dicts containing id, title, and score
        """
        # Phase 1: Stub implementation
        return [
            {"id": "stub-1", "title": f"Sample: {query}", "score": 0.95},
            {"id": "stub-2", "title": "Related Knowledge", "score": 0.85},
        ]
