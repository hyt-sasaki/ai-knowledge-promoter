"""Delete knowledge tool implementation."""

from ..domain.repositories import KnowledgeRepository


def register(mcp, repository: KnowledgeRepository):
    """Register delete_knowledge tool to the MCP server.

    Args:
        mcp: The MCP server instance
        repository: Knowledge repository for deletion
    """

    @mcp.tool
    def delete_knowledge(id: str) -> dict:
        """Delete knowledge from the system.

        Args:
            id: The ID of the knowledge to delete

        Returns:
            A dict containing status and id

        Raises:
            ValueError: If id is empty or not provided
        """
        if not id or not id.strip():
            raise ValueError("id is required")

        # Delete via repository
        deleted = repository.delete(id)

        if deleted:
            return {
                "status": "deleted",
                "id": id,
            }
        else:
            return {
                "status": "not_found",
                "id": id,
            }
