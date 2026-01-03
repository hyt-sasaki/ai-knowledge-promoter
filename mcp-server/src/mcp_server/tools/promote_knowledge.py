"""Promote knowledge tool implementation."""

from ..domain.repositories import KnowledgeRepository


def register(mcp, repository: KnowledgeRepository):
    """Register promote_knowledge tool to the MCP server.

    Args:
        mcp: The MCP server instance
        repository: Knowledge repository for persistence
    """

    @mcp.tool
    def promote_knowledge(id: str = "") -> dict:
        """Promote a draft knowledge to proposed status.

        This tool transitions a personal/draft knowledge to personal/proposed
        status, making it ready for team review and promotion.

        Args:
            id: The ID of the knowledge to promote (required)

        Returns:
            A dict containing status, id, and current_status

        Raises:
            ValueError: If id is empty, knowledge not found, or not in draft status
        """
        if not id or not id.strip():
            raise ValueError("id is required")

        # Get current knowledge
        knowledge = repository.get(id)
        if knowledge is None:
            raise ValueError("knowledge not found")

        # Validate current status
        if knowledge.status != "draft":
            raise ValueError("only draft knowledge can be promoted")

        # Update status to proposed
        updated = repository.update_status(id, "proposed")

        return {
            "status": "promoted",
            "id": updated.id,
            "current_status": updated.status,
        }
