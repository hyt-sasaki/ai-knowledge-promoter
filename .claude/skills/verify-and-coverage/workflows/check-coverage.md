# カバレッジチェックワークフロー

## 目的

仕様書（spec.md）の各RequirementとScenarioが、テスト（verify.md/ユニットテスト）でカバーされているかを分析します。

## 前提条件

- 仕様書（spec.md）が存在すること
- verify.mdが作成済みであること

## 手順

### Step 1: テンプレートをコピー

```bash
cp .claude/skills/verify-and-coverage/templates/coverage-template.md coverage.md
```

### Step 2: 仕様から要件を抽出

spec.mdから以下を抽出します：

1. **Requirements（要件）**: 機能要件のリスト
2. **Scenarios（シナリオ）**: 各要件のテストシナリオ

### Step 3: テストとのマッピング

各シナリオを以下のいずれかにマッピング：

| マッピング先 | 判定基準 |
|-------------|----------|
| verify.md | 外部依存（DB/API/ファイル）、複数コンポーネント結合 |
| ユニットテスト | 純粋関数、ビジネスロジック、バリデーション |
| Auto-Test Targets | 後続ステップで実装予定 |

### Step 4: カバレッジ確認

coverage.mdを確認し、以下をチェック：

- 「Uncovered Items」セクションが空であること
- すべてのRequirementが「Covered」または「Auto-Test Targets」に記載

### Step 5: ブロッキングルール

以下のいずれかに該当する場合、次のステップに進めません：

- 「Not Covered」が残っている
- 「Auto-Test Targets」に明示的に記載されていない未カバー項目がある

## 詳細ガイド

→ [coverage-check.md](../references/coverage-check.md)

## テンプレート

→ [coverage-template.md](../templates/coverage-template.md)
