# Change: ナレッジ昇格とアーカイブ機能の追加

## Why

Phase 2で実装した個人ナレッジの永続化・検索に続き、ナレッジを「提案」状態に遷移させる機能と、昇格完了時に元ナレッジをアーカイブする仕組みを追加する。

これにより、個人ナレッジがチームナレッジに昇格する際のライフサイクル管理が可能になる。

## What Changes

- `promote_knowledge` ツール追加（ステータスを `draft` → `proposed` に変更）
- KnowledgeRepository 拡張
  - `find_by_github_path(path: str) -> Knowledge | None`
  - `find_by_pr_url(url: str) -> Knowledge | None`
  - `update_status(id: str, status: str, **kwargs) -> Knowledge`
- `archived_knowledge` コレクション作成
- `ArchivedKnowledge` モデル実装
- `ArchivedKnowledgeRepository` 実装
- `archive` メソッド（昇格完了時に元ナレッジをアーカイブ）

## Impact

- Affected specs: knowledge-gateway
- Affected code:
  - `mcp-server/src/mcp_server/domain/models.py`
  - `mcp-server/src/mcp_server/domain/repositories.py`
  - `mcp-server/src/mcp_server/infrastructure/vector_search.py`
  - `mcp-server/src/mcp_server/tools/promote_knowledge.py` (新規)
  - `mcp-server/src/mcp_server/main.py`
- New files:
  - `mcp-server/src/mcp_server/infrastructure/archive_repository.py`
  - `mcp-server/tests/test_promote_knowledge.py`
  - `mcp-server/tests/test_archive_repository.py`
- Infrastructure changes:
  - `archived_knowledge` コレクション作成
