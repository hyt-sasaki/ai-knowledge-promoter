# Change: Firestore永続化による個人ナレッジの保存・検索

## Why

Phase 1ではスタブ実装だったsave_knowledge/search_knowledgeツールを、
Firestoreを使って実際にデータを永続化・検索できるようにする。
これにより開発者は日々のコーディング中に得た断片的なナレッジを蓄積できる。

また、Cloud Run Invoker認証を有効化し、セキュアなアクセス制御を実現する。

## What Changes

- save_knowledgeツールがFirestoreにナレッジを永続化する
- search_knowledgeツールがFirestoreから部分一致検索を行う
- Repositoryパターンによるインフラ層の抽象化（将来のデータストア変更に備える）
- Cloud Run認証を`--no-allow-unauthenticated`に変更
- ローカルからは`gcloud run services proxy`で接続
- **BREAKING**: スタブ実装からFirestore依存に変更（環境設定が必要）

## Impact

- Affected specs: knowledge-gateway
- Affected code:
  - `mcp-server/src/mcp_server/tools/save_knowledge.py`
  - `mcp-server/src/mcp_server/tools/search_knowledge.py`
  - `mcp-server/pyproject.toml`
- New files:
  - `mcp-server/src/mcp_server/domain/__init__.py`
  - `mcp-server/src/mcp_server/domain/models.py`（Knowledge, SearchResult dataclass）
  - `mcp-server/src/mcp_server/domain/repositories.py`（KnowledgeRepository Protocol）
  - `mcp-server/src/mcp_server/infrastructure/__init__.py`
  - `mcp-server/src/mcp_server/infrastructure/firestore.py`（FirestoreKnowledgeRepository）
- Updated docs:
  - `docs/roadmap.md`（将来のVertex AI Search計画追記）
  - `infra/README.md`（Phase 2インフラセットアップ手順追加）
- Infrastructure changes:
  - Firestore API有効化
  - Firestoreデータベース作成（Native mode, asia-northeast1）
  - Cloud Run IAM設定（roles/datastore.user付与）
  - Cloud Run認証設定変更（--no-allow-unauthenticated）
