# Tasks: ナレッジ昇格とアーカイブ機能の追加

垂直TDD: インフラ先行型パターンB

## 0. 提案フェーズ（Stage 1: Creating Changes）

- [x] 0.1 proposal.md作成
- [x] 0.2 tasks.md作成
- [x] 0.3 spec delta作成（specs/knowledge-gateway/spec.md）
- [x] 0.4 `openspec validate add-promote-and-archive --strict`
- [x] 0.5 **PR #1作成** https://github.com/hyt-sasaki/ai-knowledge-promoter/pull/18

---

## 1. インフラ基盤整備（Stage 2: PR #2a デプロイ基盤）

- [x] 1.1 scripts/create_archived_collection.py作成
- [x] 1.2 archived-knowledgeコレクション作成実行
- [x] 1.3 infra/README.md更新（archived-knowledgeコレクション作成手順追加）
- [x] 1.4 **PR #2a作成** https://github.com/hyt-sasaki/ai-knowledge-promoter/pull/19

---

## 2. スケルトン実装（Stage 2: PR #2b スケルトン）

### 2.1 verify.md作成
- [x] 2.1.1 verify.md作成（Runme.dev形式）
- [x] 2.1.2 REDステータス確認（promote_knowledge未実装のためRED）

### 2.2 モデル・Repository拡張
- [x] 2.2.1 ArchivedKnowledge モデル追加（domain/models.py）
- [x] 2.2.2 KnowledgeRepository Protocol拡張
  - find_by_github_path
  - find_by_pr_url
  - update_status
- [x] 2.2.3 ArchivedKnowledgeRepository Protocol追加（domain/repositories.py）
- [x] 2.2.4 VectorSearchKnowledgeRepository に新メソッド実装
- [x] 2.2.5 VectorSearchArchivedKnowledgeRepository 実装（infrastructure/archive_repository.py）

### 2.3 ツール実装
- [x] 2.3.1 promote_knowledge.py作成（スケルトン）
- [ ] 2.3.2 main.pyにツール登録

### 2.4 GREEN確認
- [ ] 2.4.1 GREENステータス確認（verify.md全パス）
- [ ] 2.4.2 **PR #2b作成**

---

## 3. ロジック実装（Stage 2: PR #3+）

- [ ] 3.1 promote_knowledge バリデーションロジック
  - personal/draftのみ昇格可能
  - 存在しないIDエラー
- [ ] 3.2 ユニットテスト追加
  - test_promote_knowledge.py
  - test_archive_repository.py
  - test_models.py（ArchivedKnowledge）
- [ ] 3.3 **PR #3作成**

---

## 4. 垂直統合チェック・アーカイブ（Stage 3: PR #N）

- [ ] 4.1 promote → search で proposed 状態確認
- [ ] 4.2 全テスト検証
- [ ] 4.3 `openspec archive add-promote-and-archive --yes`
- [ ] 4.4 verify.md / coverage.md 正式版昇格
- [ ] 4.5 **PR #N作成**
