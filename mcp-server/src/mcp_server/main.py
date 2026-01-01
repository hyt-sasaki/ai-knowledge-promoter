"""Minimal HTTP server for Cloud Run health checks."""

import os

from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.routing import Route


async def health(request):
    """Health check endpoint for Cloud Run."""
    return PlainTextResponse("OK")


app = Starlette(
    routes=[
        Route("/health", health, methods=["GET"]),
    ]
)


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
