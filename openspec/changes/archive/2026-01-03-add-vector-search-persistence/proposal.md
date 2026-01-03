# Change: Vector Search 2.0による個人ナレッジの永続化と検索

## Why

Phase 1ではスタブ実装だったsave_knowledge/search_knowledgeツールを、
Vertex AI Vector Search 2.0を使って実際にデータを永続化・検索できるようにする。
これにより開発者は日々のコーディング中に得た断片的なナレッジを蓄積し、
**セマンティック検索**で関連するナレッジを即座に発見できる。

### Vector Search 2.0を選択した理由

- **統合データストア**: ドキュメントとベクトルを一元管理（Firestore不要）
- **Auto-Embeddings**: Gemini Embeddingsを自動適用（手動ベクトル化不要）
- **ハイブリッド検索**: セマンティック検索 + 全文検索 + キーワード検索
- **インフラ自動管理**: シャード・レプリカ設定が不要
- **Public Preview中は無料**: 実験的プロジェクトに適合

また、Cloud Run Invoker認証を有効化し、セキュアなアクセス制御を実現する。

## What Changes

- save_knowledgeツールがVector Search 2.0 Collectionにナレッジを永続化する
- search_knowledgeツールがセマンティック検索を実行する
- delete_knowledgeツールを新規追加（ナレッジの削除機能）
- Repositoryパターンによるインフラ層の抽象化（将来のデータストア変更に備える）
- Cloud Run認証を`--no-allow-unauthenticated`に変更
- ローカルからは`gcloud run services proxy`で接続
- **BREAKING**: スタブ実装からVector Search 2.0依存に変更（環境設定が必要）
- **BREAKING**: save_knowledgeのtitleパラメータがオプションに変更（未指定時はcontentの先頭30文字を使用）
- **BREAKING**: search_knowledgeの戻り値にcontentフィールドを追加

## Impact

- Affected specs: knowledge-gateway
- Affected code:
  - `mcp-server/src/mcp_server/tools/save_knowledge.py`
  - `mcp-server/src/mcp_server/tools/search_knowledge.py`
  - `mcp-server/src/mcp_server/tools/delete_knowledge.py`（新規）
  - `mcp-server/pyproject.toml`
- New files:
  - `mcp-server/src/mcp_server/domain/__init__.py`
  - `mcp-server/src/mcp_server/domain/models.py`（Knowledge, SearchResult dataclass）
  - `mcp-server/src/mcp_server/domain/repositories.py`（KnowledgeRepository Protocol）
  - `mcp-server/src/mcp_server/infrastructure/__init__.py`
  - `mcp-server/src/mcp_server/infrastructure/vector_search.py`（VectorSearchKnowledgeRepository）
  - `openspec/changes/add-vector-search-persistence/verify.md`（垂直TDD検証手順）
- Updated docs:
  - `docs/roadmap.md`（Phase 2をVector Search 2.0に変更、Phase 2.5を削除）
  - `openspec/project.md`（InfrastructureセクションをVector Search 2.0に更新）
  - `infra/README.md`（Phase 2インフラセットアップ手順追加）
- Infrastructure changes:
  - Vector Search API有効化
  - AI Platform API有効化
  - Vector Search Collection作成
  - Cloud Run IAM設定
  - Cloud Run認証設定変更（--no-allow-unauthenticated）
