# Tasks: ナレッジ昇格とアーカイブ機能の追加

> ⚠️ **このタスクは using-vertical-tdd スキルに従って作業しています**
>
> 再開時は必ず `.claude/skills/using-vertical-tdd/SKILL.md` を参照してください。
> 各ステージの詳細ワークフローは下記リンクを確認してください。

パターン: B（インフラ先行型）

---

## 0. 提案フェーズ（Stage 1: Creating Changes）

> 📖 参照: [step1-proposal.md](.claude/skills/using-vertical-tdd/workflows/step1-proposal.md)

| Branch | `feat/add-promote-and-archive` |
|--------|--------------------------------|

- [x] 0.1 proposal.md作成
- [x] 0.2 tasks.md作成
- [x] 0.3 spec delta作成（specs/knowledge-gateway/spec.md）
- [x] 0.4 `openspec validate add-promote-and-archive --strict`
- [x] 0.5 **PR #1作成** https://github.com/hyt-sasaki/ai-knowledge-promoter/pull/18

---

## 1. インフラ基盤整備（Stage 2: PR #2a デプロイ基盤）

> 📖 参照: [step3-skeleton-green.md](.claude/skills/using-vertical-tdd/workflows/step3-skeleton-green.md)

| Branch | `feat/add-archived-collection` |
|--------|--------------------------------|

- [x] 1.1 scripts/create_archived_collection.py作成
- [x] 1.2 archived-knowledgeコレクション作成実行
- [x] 1.3 infra/README.md更新（archived-knowledgeコレクション作成手順追加）
- [x] 1.4 **PR #2a作成** https://github.com/hyt-sasaki/ai-knowledge-promoter/pull/19

---

## 2. スケルトン実装（Stage 2: PR #2b スケルトン）

> 📖 参照: [step2-runbook-red.md](.claude/skills/using-vertical-tdd/workflows/step2-runbook-red.md), [step3-skeleton-green.md](.claude/skills/using-vertical-tdd/workflows/step3-skeleton-green.md)

| Branch | `feat/add-promote-and-archive-skeleton` |
|--------|----------------------------------------|

> **スケルトン原則**: シグネチャと型定義のみ。中身はハードコード/ダミー。
> ビジネスロジック・実際のDB操作は Phase 3 で実装。

### 2.1 verify.md作成
- [x] 2.1.1 verify.md作成（Runme.dev形式）
- [x] 2.1.2 REDステータス確認

### 2.2 モデル・Repository スケルトン
- [x] 2.2.1 ArchivedKnowledge モデル追加（型定義のみ）
- [x] 2.2.2 KnowledgeRepository Protocol拡張（シグネチャのみ）
  - find_by_github_path
  - find_by_pr_url
  - update_status
- [x] 2.2.3 ArchivedKnowledgeRepository Protocol追加（シグネチャのみ）
- [x] 2.2.4 VectorSearchKnowledgeRepository スケルトン（中身はダミー: return None）
- [x] 2.2.5 VectorSearchArchivedKnowledgeRepository スケルトン（中身はダミー）

### 2.3 ツール スケルトン
- [x] 2.3.1 promote_knowledge.py スケルトン（ハードコードレスポンス）
- [x] 2.3.2 main.pyにツール登録

### 2.4 GREEN確認
- [x] 2.4.1 GREENステータス確認（verify.md全パス）
- [x] 2.4.2 **PR #2b作成** https://github.com/hyt-sasaki/ai-knowledge-promoter/pull/21

---

## 3. ロジック実装（Stage 2: PR #3+）

> 📖 参照: [step4-logic-meat.md](.claude/skills/using-vertical-tdd/workflows/step4-logic-meat.md)

| Branch | `feat/add-promote-and-archive-skeleton` |
|--------|----------------------------------------|

> **ユニットTDDサイクル**: Red-Green-Refactor を各機能ごとに繰り返す。
> テストケースは事前合意（assert Falseパターン）で過剰生成を防止。

### 3.1 テストケース合意フェーズ
- [x] 3.1.1 Auto-Test Targets（verify.md）を確認
- [x] 3.1.2 テスト選定制約を適用（C1網羅、同値分割、優先順位）
- [x] 3.1.3 `assert False` テストファイル作成
  - test_promote_knowledge.py
  - test_archive_repository.py
  - test_models.py（ArchivedKnowledge）
- [x] 3.1.4 テストケース合意確認

### 3.2 promote_knowledge ロジック実装
- [x] 3.2.1 test_promote_success → 実装（Red-Green-Refactor）
- [x] 3.2.2 test_promote_not_found → 実装
- [x] 3.2.3 test_promote_invalid_state → 実装
- [x] 3.2.4 test_promote_empty_id → 実装

### 3.3 Repository 本実装
- [x] 3.3.1 VectorSearchKnowledgeRepository.update_status 本実装
- [x] 3.3.2 VectorSearchArchivedKnowledgeRepository.save 本実装

### 3.4 検証
- [x] 3.4.1 ユニットテスト全パス（46件）
- [x] 3.4.2 verify.md GREEN維持確認
- [x] 3.4.3 **PR #3作成** https://github.com/hyt-sasaki/ai-knowledge-promoter/pull/22

---

## 4. 垂直統合チェック・アーカイブ（Stage 3: PR #N）

> 📖 参照: [step5-archive-release.md](.claude/skills/using-vertical-tdd/workflows/step5-archive-release.md)

| Branch | `release/add-promote-and-archive` |
|--------|-----------------------------------|

- [x] 4.1 promote → search で proposed 状態確認
- [x] 4.2 全テスト検証（ユニットテスト46件パス + verify.md GREEN）
- [x] 4.3 `openspec archive add-promote-and-archive --yes`
- [x] 4.4 verify.md / coverage.md 正式版昇格
- [x] 4.5 **PR #23作成** https://github.com/hyt-sasaki/ai-knowledge-promoter/pull/23
