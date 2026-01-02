# Tasks: Firestore永続化による個人ナレッジの保存・検索

垂直TDD: インフラ先行型パターンB

## 0. 提案フェーズ（Stage 1: Creating Changes）

- [x] 0.1 proposal.md作成
- [x] 0.2 design.md作成
- [x] 0.3 tasks.md作成
- [x] 0.4 spec delta作成（specs/knowledge-gateway/spec.md）
- [x] 0.5 `openspec validate add-firestore-persistence --strict`
- [x] 0.6 docs/roadmap.md更新（Vertex AI Search計画追記）
- [x] 0.7 **PR #1作成**

## 1. インフラ基盤整備（Stage 2: PR #2a デプロイ基盤）

- [ ] 1.1 infra/README.md更新（Phase 2セクション追加）
  - Firestore API有効化手順
  - Firestoreデータベース作成手順
  - Cloud Run認証設定変更手順
  - IAM設定手順
  - gcloud proxy接続手順
- [ ] 1.2 Firestore API有効化実行
- [ ] 1.3 Firestoreデータベース作成実行
  - database: (default)
  - location: asia-northeast1
  - type: firestore-native
- [ ] 1.4 Cloud Run IAM設定（roles/datastore.user付与）
- [ ] 1.5 Cloud Run認証設定変更（--no-allow-unauthenticated）
- [ ] 1.6 gcloud proxy動作確認
- [ ] 1.7 **PR #2a作成**

## 2. スケルトン実装（Stage 2: PR #2b スケルトン）

- [ ] 2.1 verify.md作成（Runme.dev形式）
- [ ] 2.2 REDステータス確認
- [ ] 2.3 google-cloud-firestore依存をpyproject.tomlに追加
- [ ] 2.4 domain/パッケージ作成（__init__.py含む）
- [ ] 2.5 domain/models.py作成（Knowledge, SearchResult dataclass）
- [ ] 2.6 domain/repositories.py作成（KnowledgeRepository Protocol: save, search, get）
- [ ] 2.7 infrastructure/パッケージ作成（__init__.py含む）
- [ ] 2.8 infrastructure/firestore.py作成（FirestoreKnowledgeRepository）
- [ ] 2.9 save_knowledge.pyをRepository経由で保存に更新
- [ ] 2.10 search_knowledge.pyをRepository経由で検索に更新
- [ ] 2.11 GREENステータス確認（verify.md全パス）
- [ ] 2.12 **PR #2b作成**

## 3. ロジック実装（Stage 2: PR #3 ロジック）

- [ ] 3.1 schema_version, updated_at, user_id等の自動付与
- [ ] 3.2 前方一致検索クエリの実装
- [ ] 3.3 検索結果のページネーション対応
- [ ] 3.4 エラーハンドリング強化
- [ ] 3.5 ユニットテスト追加
- [ ] 3.6 **PR #3作成**

## 4. 垂直統合チェック・リリース（Stage 3: PR #N アーカイブ）

- [ ] 4.1 保存したナレッジが検索結果として返ってくるか確認
- [ ] 4.2 全テスト検証
- [ ] 4.3 `openspec archive add-firestore-persistence --yes`
- [ ] 4.4 **PR #N作成**
