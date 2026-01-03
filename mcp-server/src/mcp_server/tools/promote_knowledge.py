"""Promote knowledge tool implementation.

Skeleton implementation for Phase 2. Full implementation in Phase 3.
"""

from ..domain.repositories import KnowledgeRepository


def register(mcp, repository: KnowledgeRepository):
    """Register promote_knowledge tool to the MCP server.

    Args:
        mcp: The MCP server instance
        repository: Knowledge repository for persistence
    """

    @mcp.tool
    def promote_knowledge(id: str = "") -> dict:
        """Promote knowledge from draft to proposed status.

        Args:
            id: The ID of the knowledge to promote

        Returns:
            A dict containing status and id

        Raises:
            ValueError: If id is empty or not provided
        """
        if not id or not id.strip():
            raise ValueError("id is required")

        # Skeleton implementation: return hardcoded response
        # Full implementation in Phase 3 will:
        # 1. Check if knowledge exists
        # 2. Check if knowledge is in personal/draft state
        # 3. Update status to "proposed"
        return {
            "status": "proposed",
            "id": id,
        }
