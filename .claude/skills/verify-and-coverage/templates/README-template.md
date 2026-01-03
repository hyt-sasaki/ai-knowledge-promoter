# Change: [機能名/change-id]

## 概要

[このchangeの簡単な説明]

## 検証

### プロジェクトルートから実行

```bash {"excludeFromRunAll":"true"}
runme run --all --filename openspec/changes/<change-id>/verify.md
```

### このディレクトリから実行

```sh {"name":"<prefix>-verify-all"}
runme run --all --filename verify.md
```

### 個別のテストを実行

```bash {"excludeFromRunAll":"true"}
# 利用可能なテスト一覧
runme list --filename verify.md

# 個別実行例
runme run <prefix>-setup-env --filename verify.md
runme run <prefix>-test-health --filename verify.md
```

詳細は `verify.md` を参照してください。

## ファイル構成

- `spec.md` - 仕様書
- `verify.md` - 統合テスト（Runme.dev形式）
- `coverage.md` - カバレッジ分析（オプション）

## 注意事項

- `<prefix>`は`change-id`または機能名に置き換えてください（例: `add-auth`）
- コマンド名はプロジェクト内でユニークである必要があります
