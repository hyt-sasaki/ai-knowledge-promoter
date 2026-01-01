# Knowledge MCP Server

Knowledge sharing MCP server for Claude Code.

## Development

```sh {"name":"install-deps"}
uv sync
```

```sh {"name":"run-local"}
uv run python -m mcp_server.main
```

```sh {"name":"run-tests"}
uv run pytest
```

## Deployment

See [../infra/README.md](../infra/README.md) for deployment instructions.
