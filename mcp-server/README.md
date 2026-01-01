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

Run individual tasks with `runme run <task-name>` or use categories:
- `runme run --category check` - Run all check tasks
- `runme run --category fix` - Run all fix tasks

### Check Tasks (category: check)

```sh {"name":"lint-check","category":"check"}
uv run ruff check src/
```

```sh {"name":"format-check","category":"check"}
uv run ruff format --check src/
```

```sh {"name":"type-check","category":"check"}
uv run ty check src/
```

```sh {"name":"check-all","category":"check"}
uv run ruff check src/ && uv run ruff format --check src/ && uv run ty check src/
```

### Fix Tasks (category: fix)

```sh {"name":"lint-fix","category":"fix"}
uv run ruff check --fix src/
```

```sh {"name":"format","category":"fix"}
uv run ruff format src/
```

## Deployment

See [../infra/README.md](../infra/README.md) for deployment instructions.
