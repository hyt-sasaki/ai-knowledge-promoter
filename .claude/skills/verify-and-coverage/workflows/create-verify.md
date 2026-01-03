# verify.md作成ワークフロー

## 目的

仕様書（spec.md等）のシナリオを、Runme.dev形式の実行可能テストドキュメントに変換します。

## 前提条件

- 仕様書（spec.md等）が存在すること
- テスト対象のシステムが定義されていること

## 手順

### Step 1: テンプレートをコピー

```bash
cp .claude/skills/verify-and-coverage/templates/verify-template.md verify.md
```

### Step 2: 仕様からシナリオを抽出

spec.mdから以下を抽出します：

1. **Requirements（要件）**: 機能要件のリスト
2. **Scenarios（シナリオ）**: GIVEN/WHEN/THEN形式のテストケース

### Step 3: コードブロックに名前を付ける

Runme.devで実行するため、各コードブロックに `{"name":"..."}` 属性を追加します：

```markdown
```sh {"name":"test-create-user"}
curl -X POST http://localhost:3000/api/users ...
# 期待値: 201 Created
```
```

### Step 4: セクション構成

1. **Setup**: テスト前の環境準備
2. **Normal Path**: 正常系テスト
3. **Edge Cases**: 異常系・境界値テスト
4. **Cleanup**: テスト後のクリーンアップ
5. **Verify All**: 一括実行スクリプト

### Step 5: RED確認

verify.mdがREDステータス（失敗）であることを確認：

```bash
runme run verify-all --filename verify.md
# 期待: テストが失敗する（未実装のため）
```

## 詳細ガイド

→ [verify-guide.md](../references/verify-guide.md)

## テンプレート

→ [verify-template.md](../templates/verify-template.md)
