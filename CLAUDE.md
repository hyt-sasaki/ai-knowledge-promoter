<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->

## Conversation Guidelines
常に日本語で会話する

## 開発方法論

このプロジェクトは**垂直TDDスケルトン戦略**を採用しています。新機能開発時、提案修正時、実装再開時に自動的に適用されます。詳細なワークフローとテンプレートは `.claude/skills/using-vertical-tdd/` を参照してください。

すべての安定チェックポイントでコミットし、大きなコミットを避けます。コミット戦略の詳細は `.claude/skills/using-vertical-tdd/workflows/commit-strategy.md` を参照してください。

Progressive Disclosureにより、必要な時だけ詳細な指示が読み込まれます。

## Runme.dev規約

Runme.dev形式のマークダウン編集時は `.claude/skills/runme-conventions/` を参照してください。

## 静的解析の実行方法

### 個別タスクの実行

```bash
# リントチェック
runme run lint-check

# リント自動修正
runme run lint-fix

# フォーマットチェック
runme run format-check

# フォーマット自動修正
runme run format

# 型チェック
runme run type-check

# すべてのチェックを一括実行
runme run check-all
```

### カテゴリ別一括実行

```bash
# すべてのチェック系タスクを実行（修正なし）
runme run --category check

# すべての修正系タスクを実行
runme run --category fix
```

### コミット前の推奨フロー

1. チェック系タスクを実行して問題を確認
2. 修正系タスクを実行して自動修正
3. 再度チェック系タスクを実行して問題がないことを確認

```bash
# 1. 問題を確認
runme run --category check

# 2. 自動修正
runme run --category fix

# 3. 再確認
runme run check-all
```