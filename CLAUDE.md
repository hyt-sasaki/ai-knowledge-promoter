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

マークダウンファイルに実行可能なコードブロックを記述する際は、Runme.dev形式に従います。

### セルレベル設定

| オプション | 説明 | 例 |
|-----------|------|-----|
| `name` | タスク名（`runme run <name>`で実行） | `{"name":"deploy"}` |
| `cwd` | 作業ディレクトリ（マークダウンファイルからの相対パス） | `{"cwd":"../mcp-server"}` |
| `excludeFromRunAll` | `runme run --all`から除外 | `{"excludeFromRunAll":"true"}` |

### フォーマット

VSCode拡張機能との差分を防ぐため、コミット前に`runme fmt -w`を実行してフォーマットを適用します。

```bash
runme fmt -w --filename <target.md>
```

### 参考リンク

- [Runme Cell Level Options](https://docs.runme.dev/configuration/cell-level)