"""Knowledge sharing MCP server for Claude Code."""

import os

from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import PlainTextResponse

from .tools.save_knowledge import register as register_save_knowledge
from .tools.search_knowledge import register as register_search_knowledge

# Stateless mode for Cloud Run horizontal scaling
mcp = FastMCP("KnowledgeGateway", stateless_http=True)


@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> PlainTextResponse:
    """Health check endpoint for Cloud Run."""
    return PlainTextResponse("OK")


# Register MCP tools
register_save_knowledge(mcp)
register_search_knowledge(mcp)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    mcp.run(transport="http", host="0.0.0.0", port=port)
