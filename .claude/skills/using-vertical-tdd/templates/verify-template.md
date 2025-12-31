# Verification: [機能名]

このファイルは、実装した機能の受け入れテスト（統合テスト/E2Eテスト）をRunme.dev形式で記述します。

## 使い方

1. このテンプレートを `openspec/changes/<change-id>/verify.md` にコピー
2. `[機能名]`、`[エンドポイント]`、`[期待値]` を実際の値に置き換え
3. 各コードブロックの `{"name":"..."}` 属性を適切な名前に変更
4. `runme run verify-all` ですべてのテストを実行

詳細な実装ガイドは [workflows/verify-implementation-guide.md](../workflows/verify-implementation-guide.md) を参照してください。

---

## Setup

```sh {"name":"setup-database"}
# データベースマイグレーション実行
npm run migrate
```

```sh {"name":"start-server"}
# アプリケーション起動（バックグラウンド）
npm run dev &
sleep 3
```

```sh {"name":"setup-test-data"}
# テストデータ作成（必要な場合）
curl -X POST http://localhost:3000/api/test/setup
```

---

## Normal Path（正常系）

```sh {"name":"test-create-resource"}
# リソース作成テスト
curl -X POST http://localhost:3000/api/[エンドポイント] \
  -H "Content-Type: application/json" \
  -d '{
    "key1": "value1",
    "key2": "value2"
  }'

# 期待値:
# ステータスコード: 201
# レスポンス: {"id": "...", "key1": "value1", "key2": "value2"}
```

```sh {"name":"test-get-resource"}
# リソース取得テスト
RESOURCE_ID=$(curl -s -X POST http://localhost:3000/api/[エンドポイント] ... | jq -r '.id')
curl -X GET http://localhost:3000/api/[エンドポイント]/$RESOURCE_ID

# 期待値:
# ステータスコード: 200
# レスポンス: {"id": "...", "key1": "value1", ...}
```

```sh {"name":"test-update-resource"}
# リソース更新テスト
RESOURCE_ID=$(curl -s -X POST ... | jq -r '.id')
curl -X PUT http://localhost:3000/api/[エンドポイント]/$RESOURCE_ID \
  -H "Content-Type: application/json" \
  -d '{"key1": "updated_value"}'

# 期待値:
# ステータスコード: 200
# レスポンス: {"id": "...", "key1": "updated_value", ...}
```

```sh {"name":"test-list-resources"}
# リソース一覧取得テスト
curl -X GET http://localhost:3000/api/[エンドポイント]

# 期待値:
# ステータスコード: 200
# レスポンス: [{"id": "...", ...}, ...]
```

```sh {"name":"test-delete-resource"}
# リソース削除テスト
RESOURCE_ID=$(curl -s -X POST ... | jq -r '.id')
curl -X DELETE http://localhost:3000/api/[エンドポイント]/$RESOURCE_ID

# 期待値:
# ステータスコード: 204
```

---

## Edge Cases（異常系）

```sh {"name":"test-invalid-input"}
# 無効な入力テスト
curl -X POST http://localhost:3000/api/[エンドポイント] \
  -H "Content-Type: application/json" \
  -d '{"email": "invalid-format"}'

# 期待値:
# ステータスコード: 400
# レスポンス: {"error": "validation_failed", "message": "..."}
```

```sh {"name":"test-missing-required-field"}
# 必須フィールド欠落テスト
curl -X POST http://localhost:3000/api/[エンドポイント] \
  -H "Content-Type: application/json" \
  -d '{"key1": "value1"}'

# 期待値:
# ステータスコード: 400
# レスポンス: {"error": "validation_failed", "message": "Missing required field"}
```

```sh {"name":"test-not-found"}
# 存在しないリソース取得テスト
curl -X GET http://localhost:3000/api/[エンドポイント]/non-existent-id

# 期待値:
# ステータスコード: 404
# レスポンス: {"error": "not_found"}
```

```sh {"name":"test-unauthorized-access"}
# 未認証アクセステスト
curl -X GET http://localhost:3000/api/protected/resource

# 期待値:
# ステータスコード: 401
# レスポンス: {"error": "unauthorized"}
```

---

## Cleanup

```sh {"name":"cleanup-test-data"}
# テストデータクリーンアップ
npm run test:cleanup
```

```sh {"name":"stop-server"}
# サーバー停止
pkill -f "npm run dev"
```

---

## Verify All（一括実行）

```sh {"name":"verify-all"}
echo "🚀 Starting verification..."

# Setup
runme run setup-database
runme run start-server
runme run setup-test-data

# Normal Path
echo "✅ Testing normal path..."
runme run test-create-resource
runme run test-get-resource
runme run test-update-resource
runme run test-list-resources
runme run test-delete-resource

# Edge Cases
echo "✅ Testing edge cases..."
runme run test-invalid-input
runme run test-missing-required-field
runme run test-not-found
runme run test-unauthorized-access

# Cleanup
echo "🧹 Cleaning up..."
runme run cleanup-test-data
runme run stop-server

echo "✅✅✅ All tests completed ✅✅✅"
```
