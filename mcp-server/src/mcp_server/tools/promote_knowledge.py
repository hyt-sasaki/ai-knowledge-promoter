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
            ValueError: If knowledge is not found
            ValueError: If knowledge is not in draft status
        """
        if not id or not id.strip():
            raise ValueError("id is required")

        # 1. Check if knowledge exists
        knowledge = repository.get(id)
        if knowledge is None:
            raise ValueError("knowledge not found")

        # 2. Check if knowledge is in draft state
        if knowledge.status != "draft":
            raise ValueError("only draft knowledge can be promoted")

        # 3. Update status to "proposed"
        updated = repository.update_status(id, "proposed")
        if updated is None:
            raise ValueError("failed to update knowledge status")

        return {
            "status": updated.status,
            "id": updated.id,
        }
