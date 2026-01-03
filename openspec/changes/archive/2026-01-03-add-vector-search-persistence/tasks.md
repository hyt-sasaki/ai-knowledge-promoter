# Tasks: Vector Search 2.0による個人ナレッジの永続化と検索

垂直TDD: インフラ先行型パターンB

## 0. 提案フェーズ（Stage 1: Creating Changes）

- [x] 0.1 proposal.md作成
- [x] 0.2 design.md作成
- [x] 0.3 tasks.md作成
- [x] 0.4 spec delta作成（specs/knowledge-gateway/spec.md）
- [x] 0.5 docs/roadmap.md更新（Phase 2変更、Phase 2.5削除）
- [x] 0.6 `openspec validate add-vector-search-persistence --strict`
- [x] 0.7 **PR作成**

## 1. インフラ基盤整備（Stage 2: PR #2a デプロイ基盤）

- [x] 1.1 infra/README.md更新（Phase 2セクション追加）
  - Vector Search API有効化手順
  - AI Platform API有効化手順
  - Collection作成手順
  - Cloud Run認証設定変更手順
  - IAM設定手順
  - gcloud proxy接続手順
- [x] 1.2 Vector Search API有効化実行
- [x] 1.3 AI Platform API有効化実行
- [x] 1.4 Collection作成スクリプト作成・実行
  - collection_id: knowledge
  - location: us-central1（asia-northeast1サポート要確認）
- [x] 1.5 Cloud Run IAM設定
- [x] 1.6 Cloud Run認証設定変更（--no-allow-unauthenticated）
- [x] 1.7 gcloud proxy動作確認
- [x] 1.8 **PR作成** → PR #14

## 2. スケルトン実装（Stage 2: PR #2b スケルトン）

- [x] 2.1 verify.md作成（Runme.dev形式）
- [x] 2.2 REDステータス確認
- [x] 2.3 google-cloud-vectorsearch依存をpyproject.tomlに追加（PR #14で完了済み）
- [x] 2.4 domain/パッケージ作成（__init__.py含む）
- [x] 2.5 domain/models.py作成（Knowledge, SearchResult dataclass）
- [x] 2.6 domain/repositories.py作成（KnowledgeRepository Protocol: save, search, get, delete）
- [x] 2.7 infrastructure/パッケージ作成（__init__.py含む）
- [x] 2.8 infrastructure/vector_search.py作成（VectorSearchKnowledgeRepository）
- [x] 2.9 save_knowledge.pyをRepository経由で保存に更新
- [x] 2.10 search_knowledge.pyをRepository経由で検索に更新
- [x] 2.11 delete_knowledge.py新規作成（Repository経由で削除）
- [x] 2.12 GREENステータス確認（verify.md全パス）
- [x] 2.14 ユニットテスト追加
- [x] 2.15 エラーハンドリング強化
- [x] 2.16 **PR作成** → PR #15

## 3. Knowledgeフィールド整理（Stage 2: PR #16）

昇格フローを詳細に検討した結果、フィールド構成を以下のように変更：
- `path` → `github_path` にリネーム（意図明確化）
- `pr_url` 追加（昇格PR URL）
- `promoted_from_id` 追加（昇格元ID）
- アーカイブ専用コレクション方式を採用（Phase 3/4で実装）

- [x] 3.1 OpenSpecドキュメント更新
  - [x] design.md: データモデル更新、状態遷移図更新、アーカイブ方式追加
  - [x] docs/roadmap.md: データモデル表更新
- [x] 3.2 tasks.md更新・コミット
- [x] 3.3 テストコードファースト（実装より先にテストを書く）
  - [x] tests/test_models.py: 新フィールドのテスト追加
- [x] 3.4 実装更新（テストをパスさせる）
  - [x] domain/models.py: path→github_path リネーム、pr_url・promoted_from_id 追加
  - [x] infrastructure/vector_search.py: 新フィールド対応
- [x] 3.5 静的解析・テスト実行（33件パス）
- [x] 3.6 verify.md で動作確認（health, save, search, delete パス）
- [x] 3.7 **PR作成** → PR #16
- [x] 3.8 Collection スキーマ更新（Vector Search 2.0は厳格なスキーマバリデーション）
  - [x] delete_collection.py 作成
  - [x] create_collection.py のスキーマ更新（path→github_path, pr_url, promoted_from_id追加）
  - [x] 既存 Collection 削除・新 Collection 作成実行
  - [x] infra/README.md 更新（Collection 再作成手順追記）
  - [x] roadmap.md に Phase 3/4 のarchived_knowledge情報を追記
- [x] 3.9 PR #16 更新
  - [x] Cloud Run 再デプロイ
  - [x] verify.md テスト実行（全パス）
  - [x] verify.md にクリーンアップタスク追加

## 4. 垂直統合チェック・リリース（Stage 3: PR #N アーカイブ）

- [x] 4.1 保存したナレッジがセマンティック検索結果として返ってくるか確認
- [x] 4.2 全テスト検証（verify.md + ユニットテスト33件パス）
- [x] 4.3 `openspec archive add-vector-search-persistence --yes`
- [x] 4.4 verify.md / coverage.md 正式版昇格
- [ ] 4.5 **PR作成**

✅✅✅ アーカイブ完了 ✅✅✅
