"""Knowledge sharing MCP server for Claude Code."""

import os

from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse

from .infrastructure.vector_search import VectorSearchKnowledgeRepository
from .tools.delete_knowledge import register as register_delete_knowledge
from .tools.save_knowledge import register as register_save_knowledge
from .tools.search_knowledge import register as register_search_knowledge

# Stateless mode for Cloud Run horizontal scaling
mcp = FastMCP("KnowledgeGateway", stateless_http=True)


@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> JSONResponse:
    """Health check endpoint for Cloud Run."""
    return JSONResponse({"status": "healthy"})


# Initialize repository with DI
repository = VectorSearchKnowledgeRepository()

# Register MCP tools with repository
register_save_knowledge(mcp, repository)
register_search_knowledge(mcp, repository)
register_delete_knowledge(mcp, repository)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    mcp.run(transport="http", host="0.0.0.0", port=port)
