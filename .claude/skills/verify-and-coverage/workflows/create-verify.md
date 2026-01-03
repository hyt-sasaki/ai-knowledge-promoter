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
cp .claude/skills/verify-and-coverage/templates/README-template.md README.md
```

### Step 2: 仕様からシナリオを抽出

spec.mdから以下を抽出します：

1. **Requirements（要件）**: 機能要件のリスト
2. **Scenarios（シナリオ）**: GIVEN/WHEN/THEN形式のテストケース

### Step 3: コードブロックに名前を付ける

Runme.devで実行するため、各コードブロックに `{"name":"<prefix>-..."}` 属性を追加します。

**重要**: `<prefix>`には`change-id`または機能名を使用してください。これによりプロジェクト内でコマンド名がユニークになります。

```markdown
```sh {"name":"add-auth-test-create-user"}
curl -X POST http://localhost:3000/api/users ...
# 期待値: 201 Created
```
```

**命名規則**:
- `<change-id>-<operation>-<target>` 形式を推奨
- 例: `add-auth-test-create-user`, `add-auth-setup-env`, `add-auth-cleanup`

### Step 4: セクション構成

1. **Setup**: テスト前の環境準備
2. **Normal Path**: 正常系テスト
3. **Edge Cases**: 異常系・境界値テスト
4. **Cleanup**: テスト後のクリーンアップ

### Step 5: README.mdで一括実行を設定

README.mdに一括実行コマンドを記述します：

```markdown
```sh {"name":"<prefix>-verify-all"}
runme run --all --filename verify.md
```
```

### Step 6: RED確認

verify.mdがREDステータス（失敗）であることを確認：

```bash
runme run --all --filename verify.md
# 期待: テストが失敗する（未実装のため）
```

## 詳細ガイド

→ [verify-guide.md](../references/verify-guide.md)

## テンプレート

→ [verify-template.md](../templates/verify-template.md)
→ [README-template.md](../templates/README-template.md)
