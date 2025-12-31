# Verification: [機能名]

このファイルは、実装した機能の受け入れテスト（**統合テスト/E2Eテスト**）をRunme.dev形式で記述します。

## テストピラミッドにおける役割

verify.mdは**統合テスト/E2Eテスト**として機能します：

- ✅ **End-to-Endフロー確認**: UI/CLI → API → DB → レスポンス
- ✅ **外部リソース依存**: 実際のDB接続、ファイルI/O、外部API
- ✅ **複数コンポーネント結合**: 認証、API、データベース等の統合動作
- ✅ **システム全体の動作確認**: 本番環境に近い状態でのテスト

**注**: ビジネスロジック、純粋関数、バリデーション等は**ユニットテスト**でカバーします。verify.mdは外部依存や結合コストが高いものに焦点を当てます。

## 使い方

1. このテンプレートを `openspec/changes/<change-id>/verify.md` にコピー
2. `[機能名]`、`[APIエンドポイント]`、`[期待値]` を実際の値に置き換え
3. 各コードブロックの `{"name":"..."}` 属性を適切な名前に変更
4. `runme list` でコマンド一覧を確認
5. `runme run verify-all` ですべてのテストを実行

## Runme.dev実行方法

### 方法1: CLI
```bash
runme list                    # コマンド一覧表示
runme run setup-database      # 個別実行
runme run verify-all          # 一括実行
```

### 方法2: TUI（対話式）
```bash
runme tui                     # 対話式メニュー起動
# 矢印キーでコマンド選択、Enterで実行
```

### 方法3: VS Code拡張機能
1. Runme拡張機能をインストール
2. このファイルを開く
3. 各コードブロックの▶ボタンをクリックで実行

---

## Setup

データベースのセットアップ、サーバー起動など、テスト実行前の準備を行います。

```sh {"name":"setup-database"}
# データベースマイグレーション実行
npm run migrate
# または: python manage.py migrate
# または: bundle exec rake db:migrate
```

```sh {"name":"start-server"}
# アプリケーション起動（バックグラウンド）
npm run dev &
# または: python main.py &
# または: bundle exec rails server &

# サーバー起動待機
sleep 3
```

```sh {"name":"setup-test-data"}
# テストデータ作成（必要な場合）
# 例: テストユーザー作成、初期データ投入等
curl -X POST http://localhost:3000/api/test/setup
```

---

## Normal Path（正常系）

通常のユースケースをテストします。

```sh {"name":"test-create-resource"}
# リソース作成テスト（例: ユーザー作成）
curl -X POST http://localhost:3000/api/[エンドポイント] \
  -H "Content-Type: application/json" \
  -d '{
    "key1": "value1",
    "key2": "value2"
  }'

# 期待値:
# ステータスコード: 201
# レスポンス: {"id": "...", "key1": "value1", "key2": "value2", "created_at": "..."}
```

```sh {"name":"test-get-resource"}
# リソース取得テスト
# 前のテストで作成したリソースのIDを使用
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
  -d '{
    "key1": "updated_value"
  }'

# 期待値:
# ステータスコード: 200
# レスポンス: {"id": "...", "key1": "updated_value", ...}
```

```sh {"name":"test-list-resources"}
# リソース一覧取得テスト
curl -X GET http://localhost:3000/api/[エンドポイント]

# 期待値:
# ステータスコード: 200
# レスポンス: [{"id": "...", ...}, {"id": "...", ...}]
```

```sh {"name":"test-delete-resource"}
# リソース削除テスト
RESOURCE_ID=$(curl -s -X POST ... | jq -r '.id')

curl -X DELETE http://localhost:3000/api/[エンドポイント]/$RESOURCE_ID

# 期待値:
# ステータスコード: 204（または200）
# レスポンス: 空（または {"message": "Deleted successfully"}）
```

---

## Edge Cases（異常系）

エラーハンドリング、バリデーション、境界値テストを行います。

```sh {"name":"test-duplicate-creation"}
# 重複作成テスト（例: 同じメールアドレスで2回ユーザー作成）
# 1回目（成功）
curl -X POST http://localhost:3000/api/[エンドポイント] \
  -H "Content-Type: application/json" \
  -d '{"email": "duplicate@example.com", ...}'

# 2回目（失敗）
curl -X POST http://localhost:3000/api/[エンドポイント] \
  -H "Content-Type: application/json" \
  -d '{"email": "duplicate@example.com", ...}'

# 期待値:
# ステータスコード: 409（Conflict）
# レスポンス: {"error": "already_exists", "message": "Email already registered"}
```

```sh {"name":"test-invalid-input"}
# 無効な入力テスト（例: メールアドレス形式不正）
curl -X POST http://localhost:3000/api/[エンドポイント] \
  -H "Content-Type: application/json" \
  -d '{
    "email": "invalid-email-format",
    "password": "SecurePass123"
  }'

# 期待値:
# ステータスコード: 400（Bad Request）
# レスポンス: {"error": "validation_failed", "message": "Invalid email format"}
```

```sh {"name":"test-missing-required-field"}
# 必須フィールド欠落テスト
curl -X POST http://localhost:3000/api/[エンドポイント] \
  -H "Content-Type: application/json" \
  -d '{
    "key1": "value1"
  }'

# 期待値:
# ステータスコード: 400
# レスポンス: {"error": "validation_failed", "message": "Missing required field: key2"}
```

```sh {"name":"test-not-found"}
# 存在しないリソース取得テスト
curl -X GET http://localhost:3000/api/[エンドポイント]/non-existent-id

# 期待値:
# ステータスコード: 404（Not Found）
# レスポンス: {"error": "not_found", "message": "Resource not found"}
```

```sh {"name":"test-unauthorized-access"}
# 未認証アクセステスト（認証が必要なエンドポイントの場合）
curl -X GET http://localhost:3000/api/protected/resource
# Authorization ヘッダーなし

# 期待値:
# ステータスコード: 401（Unauthorized）
# レスポンス: {"error": "unauthorized", "message": "Authentication required"}
```

```sh {"name":"test-forbidden-access"}
# 権限不足テスト（認可が必要なエンドポイントの場合）
curl -X DELETE http://localhost:3000/api/admin/resource \
  -H "Authorization: Bearer <non-admin-token>"

# 期待値:
# ステータスコード: 403（Forbidden）
# レスポンス: {"error": "forbidden", "message": "Insufficient permissions"}
```

---

## Cleanup

テスト後のクリーンアップを行います。

```sh {"name":"cleanup-test-data"}
# テストデータクリーンアップ
npm run test:cleanup
# または: curl -X DELETE http://localhost:3000/api/test/cleanup
# または: python scripts/cleanup_test_data.py
```

```sh {"name":"stop-server"}
# サーバー停止
pkill -f "npm run dev"
# または: pkill -f "python main.py"
# または: pkill -f "rails server"
```

---

## Verify All（一括実行）

すべてのテストを順次実行します。

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
runme run test-duplicate-creation
runme run test-invalid-input
runme run test-missing-required-field
runme run test-not-found
runme run test-unauthorized-access
runme run test-forbidden-access

# Cleanup
echo "🧹 Cleaning up..."
runme run cleanup-test-data
runme run stop-server

echo "✅✅✅ All tests completed ✅✅✅"
```

---

## 高度な使用例

### Python スクリプトでのテスト

```python {"name":"test-with-python"}
import requests

response = requests.post(
    "http://localhost:3000/api/[エンドポイント]",
    json={"key1": "value1", "key2": "value2"}
)

print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

# 期待値:
# Status: 201
# Response: {"id": "...", "key1": "value1", ...}
```

### JavaScript/TypeScript でのテスト

```typescript {"name":"test-with-typescript"}
const response = await fetch("http://localhost:3000/api/[エンドポイント]", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ key1: "value1", key2: "value2" })
});

const data = await response.json();
console.log(`Status: ${response.status}`, data);

// 期待値:
// Status: 201
// Response: {"id": "...", "key1": "value1", ...}
```

### 環境変数の使用

```sh {"name":"test-with-env"}
# .envファイルから環境変数を読み込み
export API_TOKEN=$(cat .env | grep API_TOKEN | cut -d '=' -f2)

curl -X GET http://localhost:3000/api/protected \
  -H "Authorization: Bearer $API_TOKEN"

# 期待値: 認証成功レスポンス
```

### アサーションの追加

```sh {"name":"test-with-assertion"}
RESPONSE=$(curl -s -X GET http://localhost:3000/api/[エンドポイント])

# jqでレスポンスを検証
echo $RESPONSE | jq -e '.id != null' || (echo "❌ ID is missing" && exit 1)
echo $RESPONSE | jq -e '.key1 == "expected_value"' || (echo "❌ key1 mismatch" && exit 1)

echo "✅ Assertions passed"
```

---

## トラブルシューティング

### サーバーが起動しない場合

```sh {"name":"check-server-status"}
# プロセス確認
ps aux | grep "npm run dev"

# ポート使用状況確認
lsof -i :3000

# ログ確認
tail -f server.log
```

### データベース接続エラー

```sh {"name":"check-database"}
# データベース接続テスト
psql -U postgres -c "SELECT 1"
# または: mysql -u root -p -e "SELECT 1"
# または: sqlite3 db.sqlite3 "SELECT 1"
```

### テストデータが残っている場合

```sh {"name":"force-cleanup"}
# 強制クリーンアップ
npm run test:cleanup --force
# または: DROP DATABASE test_db; CREATE DATABASE test_db;
```

---

## カスタマイズのヒント

1. **名前付きコードブロック**: `{"name":"..."}` を明確で短い名前に
2. **期待値の明記**: コメントで期待するレスポンスとステータスコードを記載
3. **環境変数**: `.env` ファイルでAPIトークン等を管理
4. **アサーション**: `jq`、`grep`、`test` コマンドで検証を追加
5. **並列実行**: 独立したテストは `&` で並列実行可能

## 参考リンク

- [Runme.dev公式ドキュメント](https://docs.runme.dev/)
- [Runme CLI Reference](https://docs.runme.dev/configuration/cli-reference)
