---
name: using-vertical-tdd
description: |
  OpenSpec駆動の垂直TDDスケルトン戦略。提案作成・技術検証・設計・実装・アーカイブの全ライフサイクルをサポート。
  使用タイミング:
  (1) 新機能開発の開始時（「新機能を追加」「〜を実装」リクエスト、OpenSpec提案がまだ存在しない場合）
  (2) 提案の修正・継続（openspec/changes/配下にファイルが存在、「提案を修正」「設計を見直し」リクエスト）
  (3) 実装の再開（tasks.mdに未完了タスクがある、「実装を続ける」「次のステップ」リクエスト）
  (4) 技術検証が必要（design.md作成前、複数技術選択肢がある、「技術検証」「ライブラリ調査」リクエスト）
  使用しない場合: バグ修正、タイポ修正、ドキュメント更新のみ、設定ファイル変更のみ
allowed-tools: Read, Bash(openspec:*), Bash(runme:*), Bash(git:*), Bash(gh pr create:*), Bash(gh pr view:*), Bash(cat:*), Bash(jq:*), Bash(rg:*), Bash(mkdir:*), WebSearch, WebFetch, mcp__plugin_context7_context7__resolve-library-id, mcp__plugin_context7_context7__query-docs
---

# 垂直TDDスケルトン戦略

## ビジョン

- **常にデプロイ可能**: すべてのPRでmainブランチにマージ可能な状態を維持
- **シフトレフト結合**: システム統合を最終段階ではなく最初のPR（スケルトン）で完了
- **AI共生**: AIアシスタントが一貫したワークフローで効率的に作業できる構造

## OpenSpecライフサイクル統合

OpenSpecの3ステージに垂直TDDステップをマッピング：

### Stage 1: Creating Changes（提案作成）

- **Step 0: Proposal** → [workflows/step0-proposal.md](workflows/step0-proposal.md)
  - OpenSpec提案の作成、インターフェース合意、tasks.md開始

- **Step 0.5: Tech Spike**（任意） → [workflows/step0.5-tech-spike.md](workflows/step0.5-tech-spike.md)
  - 技術的妥当性の検証、Context7でライブラリ調査

- **Step 0.9: Design**（任意） → [workflows/step0.9-design.md](workflows/step0.9-design.md)
  - design.mdで設計判断を文書化

### Stage 2: Implementing Changes（実装）

- **Step 1: Runbook & Red** → [workflows/step1-runbook-red.md](workflows/step1-runbook-red.md)
  - Runme.dev形式でverify.md作成、RED確認

- **Step 2: Skeleton Green** → [workflows/step2-skeleton-green.md](workflows/step2-skeleton-green.md)
  - 最小実装でGREEN、PR #1マージ（フィーチャーフラグOFF）

- **Step 3: Logic Meat** → [workflows/step3-logic-meat.md](workflows/step3-logic-meat.md)
  - ユニットTDDでロジック実装、PR #2マージ

### Stage 3: Archiving Changes（アーカイブ）

- **Step 4: Archive & Release** → [workflows/step4-archive-release.md](workflows/step4-archive-release.md)
  - 全テスト検証、アーカイブ、フィーチャーフラグ有効化、PR #3

## テンプレート

- **verify.md**: [templates/verify-template.md](templates/verify-template.md)
- **tech-spike.md**: [templates/tech-spike-template.md](templates/tech-spike-template.md)

## コミット戦略

安定チェックポイントでこまめにコミット。詳細は [workflows/commit-strategy.md](workflows/commit-strategy.md) を参照。

## 実装再開時

```bash
openspec show <change-id>
cat openspec/changes/<change-id>/tasks.md
# → tasks.mdの進捗に基づき次のステップを提案
```

## Context7統合

Step 0.5（Tech Spike）でライブラリ調査、Step 0.9（Design）でベストプラクティス調査に使用。

```bash
# MCPツール: mcp__plugin_context7_context7__resolve-library-id
# → mcp__plugin_context7_context7__query-docs
```

## 重要な原則

1. **疎通優先、ロジック後回し**: Step 2ではUIからDBまで貫通させ、ビジネスロジックは書かない
2. **フィーチャーフラグで段階的リリース**: 環境変数で制御、スケルトンはOFFでマージ
3. **3つのPRで段階的マージ**: PR #1（スケルトン）→ PR #2（ロジック）→ PR #3（リリース）
4. **verify.mdは実行可能なドキュメント**: Runme.devでそのまま実行可能

## 詳細ワークフロー

- [Step 0: Proposal](workflows/step0-proposal.md)
- [Step 0.5: Tech Spike](workflows/step0.5-tech-spike.md)
- [Step 0.9: Design](workflows/step0.9-design.md)
- [Step 1: Runbook & Red](workflows/step1-runbook-red.md)
- [Step 2: Skeleton Green](workflows/step2-skeleton-green.md)
- [Step 3: Logic Meat](workflows/step3-logic-meat.md)
- [Step 4: Archive & Release](workflows/step4-archive-release.md)

## よくある質問

→ [references/faq.md](references/faq.md)
