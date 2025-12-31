---
name: using-vertical-tdd
description: OpenSpec駆動の垂直TDDスケルトン戦略。提案作成・技術検証・設計・実装・アーカイブの全ライフサイクルをサポート。tasks.md進捗に基づき自動的に適切なステップを提案。新機能開発の開始時、提案修正時、実装再開時、技術検証時に使用。Context7で最新ライブラリ情報を調査し設計精度を向上。
allowed-tools: Read, Bash(openspec:*), Bash(runme:*), Bash(git:*), Bash(gh pr create:*), Bash(gh pr view:*), Bash(cat:*), Bash(jq:*), Bash(rg:*), Bash(mkdir:*), WebSearch, WebFetch, mcp__plugin_context7_context7__resolve-library-id, mcp__plugin_context7_context7__query-docs
---

# 垂直TDDスケルトン戦略の使用

## ビジョン

この開発方法論は3つの原則に基づいています：

- **常にデプロイ可能**: すべてのPRでmainブランチにマージ可能な状態を維持
- **シフトレフト結合**: システム統合を最終段階ではなく最初のPR（スケルトン）で完了
- **AI共生**: AIアシスタントが一貫したワークフローで効率的に作業できる構造

## このSkillの発火条件（自動判定）

このSkillは以下の状況で自動的に適用されます：

### 1. 新規開発の開始

✅ 「新機能を追加」「〜を実装」というリクエスト
✅ OpenSpec提案がまだ存在しない
✅ 新しいcapabilityの導入や既存capabilityの大幅変更

### 2. 提案の修正・継続

✅ `openspec/changes/<change-id>/`配下のファイルが存在
✅ proposal.mdやspec deltasの修正が必要
✅ 「提案を修正」「設計を見直し」というリクエスト

### 3. 実装の再開

✅ tasks.mdに未完了タスク（`- [ ]`）がある
✅ 「実装を続ける」「次のステップ」というリクエスト
✅ 作業中断後の再開時

### 4. 技術検証が必要

✅ design.mdを作成する前
✅ 複数の技術選択肢がある（ライブラリA vs B等）
✅ 「技術検証」「ライブラリ調査」というリクエスト
✅ パフォーマンスや互換性の懸念がある

### ❌ 使用しない場合

❌ バグ修正（既存仕様の復元）
❌ タイポ・フォーマット修正
❌ ドキュメント更新のみ
❌ 設定ファイルの変更のみ

## OpenSpecライフサイクルとの統合

OpenSpecの3ステージに垂直TDDステップをマッピング：

### OpenSpec Stage 1: Creating Changes（提案作成）

- **Step 0: Proposal** → [workflows/step0-proposal.md](workflows/step0-proposal.md)
  - OpenSpec提案の作成
  - インターフェース（API型、DBスキーマ）とテストシナリオの合意
  - tasks.mdでタスク進捗管理開始

- **Step 0.5: Tech Spike**（任意） → [workflows/step0.5-tech-spike.md](workflows/step0.5-tech-spike.md)
  - 技術的妥当性の検証
  - 最小限の実験コードで選択肢を比較
  - Context7で最新ライブラリ情報を調査
  - spike/results.mdに結果を記録

- **Step 0.9: Design**（任意） → [workflows/step0.9-design.md](workflows/step0.9-design.md)
  - design.mdで設計判断を文書化
  - 技術検証結果を設計に反映
  - Context7で最新ベストプラクティスを調査

### OpenSpec Stage 2: Implementing Changes（実装）

- **Step 1: Runbook & Red** → [workflows/step1-runbook-red.md](workflows/step1-runbook-red.md)
  - Runme.dev形式でverify.mdを作成
  - 期待する挙動をcURLやCLIコマンドで記述
  - RED（失敗）を確認

- **Step 2: Skeleton Green** → [workflows/step2-skeleton-green.md](workflows/step2-skeleton-green.md)
  - verify.mdがパスする最小限の実装
  - ハードコードやモック使用可
  - システム疎通を証明
  - PR #1: フィーチャーフラグOFFでマージ

- **Step 3: Logic Meat** → [workflows/step3-logic-meat.md](workflows/step3-logic-meat.md)
  - スケルトンの内部を本物のロジックに置き換え
  - ユニットTDDサイクル（Red-Green-Refactor）
  - テストピラミッド（ユニットテスト >> 統合テスト）
  - PR #2: ロジック実装をマージ

### OpenSpec Stage 3: Archiving Changes（アーカイブ）

- **Step 4: Archive & Release** → [workflows/step4-archive-release.md](workflows/step4-archive-release.md)
  - 全テストとverify.mdの最終検証
  - `openspec archive <change-id>`でアーカイブ
  - フィーチャーフラグ有効化
  - PR #3: リリース

## tasks.md進捗ベースの自動ナビゲーション

実装再開時、以下のロジックで次のステップを判定：

```python
# 疑似コード
def determine_next_step(tasks_md):
    # tasks.mdを読み込み、完了状態をチェック
    completed = parse_completed_tasks(tasks_md)

    if "proposal.md記述" not in completed:
        return "Step 0: Proposal"

    if "技術検証" in tasks and not completed:
        return "Step 0.5: Tech Spike"

    if "design.md作成" in tasks and not completed:
        return "Step 0.9: Design"

    if "verify.md作成" not in completed:
        return "Step 1: Runbook & Red"

    if "REDステータス確認" not in completed:
        return "Step 1: Runbook & Red（RED確認）"

    if "スケルトン実装" not in completed:
        return "Step 2: Skeleton Green"

    if "PR #1マージ" not in completed:
        return "Step 2: Skeleton Green（PR作成）"

    if "ロジック実装" not in completed:
        return "Step 3: Logic Meat"

    if "PR #2マージ" not in completed:
        return "Step 3: Logic Meat（PR作成）"

    if "アーカイブ" not in completed:
        return "Step 4: Archive & Release"

    return "完了"
```

## テンプレート

- **verify.md**: [templates/verify-template.md](templates/verify-template.md)
  - Runme.dev 2025形式
  - 名前付きコードブロック（`{"name":"command-name"}`）
  - runme CLI/TUI/VS Code拡張対応

- **tech-spike.md**: [templates/tech-spike-template.md](templates/tech-spike-template.md)
  - spike/results.md用テンプレート
  - 技術検証結果の記録フォーマット

## 実装再開時のコマンド

```bash
# 現在のステータス確認
openspec show <change-id>
cat openspec/changes/<change-id>/tasks.md

# tasks.mdの進捗を確認し、次のステップを判定
# → このSkillが自動的にtasks.mdを読み、次のステップを提案
```

## Context7統合パターン

### ライブラリ調査（Step 0.5で使用）

```bash
# MCPツール: mcp__plugin_context7_context7__resolve-library-id
# → mcp__plugin_context7_context7__query-docs

# 例: Next.jsのServer Components vs Client Components比較
# 1. Context7で `/vercel/next.js` を検索
# 2. 「Server Components data fetching patterns」を調査
# 3. 「Client Components hydration performance」を調査
# 4. spike/results.mdに比較結果を記録
```

### ベストプラクティス調査（Step 0.9で使用）

```bash
# 例: FastAPI認証パターン調査
# 1. Context7で `/tiangolo/fastapi` を検索
# 2. 「authentication security best practices」を調査
# 3. design.mdのセキュリティセクションに反映
```

## フィードバックループ

各ステップで以下のパターンを使用：

```bash
# 実装 → 検証 → 修正のサイクル

# Step 1: verify.md作成後
runme run verify-all  # REDを確認

# Step 2: スケルトン実装後
runme run verify-all  # GREENを確認

# Step 3: ロジック実装後
pytest tests/         # ユニットテスト
runme run verify-all  # 統合テスト

# Step 4: アーカイブ前
openspec validate <change-id> --strict  # 最終検証
```

## 重要な原則

### 1. 疎通優先、ロジック後回し

Step 2（Skeleton Green）では、UIからDBまで貫通させることを最優先とし、ビジネスロジックは一切書きません。ハードコードやモックで十分です。

### 2. フィーチャーフラグで段階的リリース

```python
FEATURE_<NAME>_ENABLED = os.getenv("FEATURE_<NAME>_ENABLED", "false") == "true"
```

環境変数で制御し、スケルトンはフィーチャーフラグOFFでマージします。

### 3. 3つのPRで段階的マージ

- **PR #1**: スケルトン（フィーチャーフラグOFF）
- **PR #2**: ロジック実装
- **PR #3**: リリース（フィーチャーフラグ有効化、アーカイブ）

### 4. verify.mdは実行可能なドキュメント

Runme.devを使用し、verify.mdをそのまま実行可能なテストスクリプトとして扱います。

## ワークフロー図

```
ユーザーストーリー
    ↓
Step 0: Proposal (OpenSpec提案作成)
    │ - openspec proposal
    │ - proposal.md + tasks.md + spec deltas
    │ - 2人でレビュー・承認
    ↓
    │ ← 技術検証が必要？
    ↓ Yes
Step 0.5: Tech Spike（技術検証）
    │ - Context7でライブラリ調査
    │ - 最小実験コード実装
    │ - spike/results.md記録
    ↓
    │ ← design.md作成が必要？
    ↓ Yes
Step 0.9: Design（設計文書化）
    │ - Context7でベストプラクティス調査
    │ - 技術検証結果を設計に反映
    │ - design.md作成
    ↓
Step 1: Runbook & Red (Runme.dev)
    │ - verify.md作成
    │ - 期待する挙動を記述
    │ - RED確認
    ↓
Step 2: Skeleton Green
    │ - 最小実装（モック/ハードコード可）
    │ - verify.mdがパス（GREEN）
    │ - PR #1: フィーチャーフラグOFFでマージ
    ↓
Step 3: Logic Meat (ユニットTDD)
    │ - ユニットテスト先行（RED）
    │ - 本実装（GREEN）
    │ - リファクタリング
    │ - PR #2: ロジック実装マージ
    ↓
Step 4: Archive & Release
    │ - 全テスト + verify.md検証
    │ - openspec archive <change-id>
    │ - フィーチャーフラグ有効化
    │ - PR #3: リリース
    ↓
本番環境
```

## 詳細ワークフロー

各ステップの詳細は、以下のファイルを参照してください：

- [Step 0: Proposal](workflows/step0-proposal.md) - 提案作成
- [Step 0.5: Tech Spike](workflows/step0.5-tech-spike.md) - 技術検証
- [Step 0.9: Design](workflows/step0.9-design.md) - 設計文書化
- [Step 1: Runbook & Red](workflows/step1-runbook-red.md) - 検証スクリプト作成
- [Step 2: Skeleton Green](workflows/step2-skeleton-green.md) - スケルトン実装
- [Step 3: Logic Meat](workflows/step3-logic-meat.md) - ロジック実装
- [Step 4: Archive & Release](workflows/step4-archive-release.md) - アーカイブとリリース

## よくある質問

**Q: なぜスケルトンを先にマージするのか？**

A: システム統合の問題を早期に発見するためです。UI、API、DB層の接続が正常に動作することを確認してからロジックを実装することで、後戻りを防ぎます。

**Q: フィーチャーフラグはどのタイミングで有効化するのか？**

A: Step 4（Archive & Release）で全テストとverify.mdが完全にパスした後、フィーチャーフラグを有効化します。

**Q: Context7はどのタイミングで使用するのか？**

A: Step 0.5（Tech Spike）でライブラリ比較、Step 0.9（Design）でベストプラクティス調査に使用します。

**Q: tasks.mdが存在しない場合はどうするのか？**

A: Step 0（Proposal）から開始し、tasks.mdを作成します。

**Q: verify.mdとユニットテストの違いは？**

A: verify.mdは統合テスト（E2Eテスト）で、実際のAPIやCLIコマンドを実行します。ユニットテストは個別の関数・メソッドのテストです。両方必要です。
