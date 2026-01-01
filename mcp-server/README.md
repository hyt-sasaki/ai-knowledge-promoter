# Knowledge MCP Server

Knowledge sharing MCP server for Claude Code.

## Development

```sh {"name":"install-deps"}
uv sync --group dev
```

```sh {"name":"run-local"}
uv run python -m mcp_server.main
```

```sh {"name":"run-tests"}
uv run pytest
```

## Static Analysis

```sh {"name":"lint-check"}
uv run ruff check src/
```

```sh {"name":"lint-fix"}
uv run ruff check --fix src/
```

```sh {"name":"format-check"}
uv run ruff format --check src/
```

```sh {"name":"format"}
uv run ruff format src/
```

```sh {"name":"type-check"}
uv run ty check src/
```

```sh {"name":"check-all"}
uv run ruff check src/ && uv run ruff format --check src/ && uv run ty check src/
```

## Deployment

See [../infra/README.md](../infra/README.md) for deployment instructions.
