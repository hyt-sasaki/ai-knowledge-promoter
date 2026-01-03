# verify.md 実装ガイド

このガイドは、[verify-template.md](../templates/verify-template.md) を使用してverify.mdを作成する際の詳細な実装ガイドです。

## テストピラミッドにおける役割

verify.mdは**統合テスト/E2Eテスト**として機能します：

- ✅ **End-to-Endフロー確認**: UI/CLI → API → DB → レスポンス
- ✅ **外部リソース依存**: 実際のDB接続、ファイルI/O、外部API
- ✅ **複数コンポーネント結合**: 認証、API、データベース等の統合動作
- ✅ **システム全体の動作確認**: 本番環境に近い状態でのテスト

**注**: ビジネスロジック、純粋関数、バリデーション等は**ユニットテスト**でカバーします。verify.mdは外部依存や結合コストが高いものに焦点を当てます。

## Runme.dev実行方法

**注**: このプロジェクトでは`mise.toml`でRunme.devを管理しています。miseが自動的にインストールするため、手動インストールは不要です。

### 方法1: CLI（コマンドライン）

個別のコマンドを実行：

```bash
runme list --filename verify.md              # コマンド一覧表示
runme run <prefix>-setup-database            # 個別実行
runme run --all --filename verify.md         # 一括実行
```

**注意**: `<prefix>`には`change-id`または機能名を使用してください（例: `add-auth-setup-database`）。

**メリット**:
- CI/CDパイプラインで使用可能
- スクリプトから呼び出し可能
- 自動化しやすい

### 方法2: TUI（対話式メニュー）

対話式メニューでコマンドを選択・実行：

```bash
runme tui                     # 対話式メニュー起動
# 矢印キーでコマンド選択、Enterで実行
```

**メリット**:
- 視覚的にコマンドを確認
- 実行結果をリアルタイム表示
- 初見のファイルでも使いやすい

### 方法3: VS Code拡張機能

1. Runme拡張機能をインストール
2. verify.mdファイルを開く
3. 各コードブロックの▶ボタンをクリックで実行
4. 実行結果がインラインで表示される

**メリット**:
- エディタ内で完結
- Markdownプレビューと実行を同時に表示
- 結果を直接ファイルに保存可能

## 名前付きコードブロックの構文

Runme.devは名前付きコードブロックを認識します：

```markdown
```sh {"name":"<prefix>-command-name"}
# コマンド内容
\```
```

- `{"name":"<prefix>-..."}` 属性が必須
- `<prefix>`には`change-id`または機能名を使用（プロジェクト内でユニークにするため）
- `runme list` でこの名前が表示される
- `runme run <prefix>-command-name` で実行可能

**命名規則**:
- `<change-id>-<operation>-<target>` 形式を推奨
- 例: `add-auth-setup-database`, `add-auth-test-create-user`, `add-auth-cleanup`

## テンプレートカスタマイズのヒント

### 1. 名前付きコードブロック

明確で短い名前を付ける（prefixを含む）：

✅ Good:
- `{"name":"add-auth-setup-database"}`
- `{"name":"add-auth-test-create-user"}`
- `{"name":"add-auth-cleanup-test-data"}`

❌ Bad:
- `{"name":"test1"}` （何のテストか不明、prefixなし）
- `{"name":"setup-database"}` （prefixなし、名前衝突の可能性）
- `{"name":"this-is-a-very-long-descriptive-name-that-is-hard-to-type"}` （長すぎる）

### 2. 期待値の明記

コメントで期待するレスポンスとステータスコードを明記：

```sh
# 期待値:
# ステータスコード: 201
# レスポンス: {"id": "...", "email": "test@example.com"}
```

### 3. 環境変数の使用

`.env` ファイルでAPIトークン等を管理：

```sh {"name":"<prefix>-test-with-env"}
# .envファイルから環境変数を読み込み
export API_TOKEN=$(cat .env | grep API_TOKEN | cut -d '=' -f2)

curl -X GET http://localhost:3000/api/protected \
  -H "Authorization: Bearer $API_TOKEN"
```

### 4. アサーションの追加

`jq`、`grep`、`test` コマンドで検証を追加：

```sh {"name":"<prefix>-test-with-assertion"}
RESPONSE=$(curl -s -X GET http://localhost:3000/api/users/123)

# jqでレスポンスを検証
echo $RESPONSE | jq -e '.id != null' || (echo "❌ ID is missing" && exit 1)
echo $RESPONSE | jq -e '.email == "test@example.com"' || (echo "❌ Email mismatch" && exit 1)

echo "✅ Assertions passed"
```

## 高度な使用例

### Python スクリプトでのテスト

```python {"name":"<prefix>-test-with-python"}
import requests

response = requests.post(
    "http://localhost:3000/api/users",
    json={"email": "test@example.com", "password": "SecurePass123"}
)

print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

# 期待値:
# Status: 201
# Response: {"id": "...", "email": "test@example.com"}
```

### JavaScript/TypeScript でのテスト

```typescript {"name":"<prefix>-test-with-typescript"}
const response = await fetch("http://localhost:3000/api/users", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ email: "test@example.com", password: "SecurePass123" })
});

const data = await response.json();
console.log(`Status: ${response.status}`, data);

// 期待値:
// Status: 201
// Response: {"id": "...", "email": "test@example.com"}
```

### 複雑なセットアップ

```sh {"name":"<prefix>-setup-with-fixtures"}
# データベースリセット
npm run db:reset

# フィクスチャデータ投入
psql -U postgres -d test_db -f fixtures/users.sql
psql -U postgres -d test_db -f fixtures/products.sql

# キャッシュクリア
redis-cli FLUSHALL

# サーバー再起動
pkill -f "npm run dev"
npm run dev &
sleep 5

echo "✅ Setup completed"
```

## トラブルシューティング

### サーバーが起動しない場合

```sh {"name":"<prefix>-check-server-status"}
# プロセス確認
ps aux | grep "npm run dev"

# ポート使用状況確認
lsof -i :3000

# ログ確認
tail -f server.log
```

**解決策**:
- ポートが既に使用されている場合: `kill -9 <PID>` でプロセスを終了
- 設定ファイルエラー: ログを確認し、設定ファイルを修正
- 依存関係不足: `npm install` または `pip install -r requirements.txt` を実行

### データベース接続エラー

```sh {"name":"<prefix>-check-database"}
# PostgreSQL接続テスト
psql -U postgres -c "SELECT 1"

# MySQL接続テスト
mysql -u root -p -e "SELECT 1"

# SQLite接続テスト
sqlite3 db.sqlite3 "SELECT 1"
```

**解決策**:
- データベースサービスが起動していない: `brew services start postgresql` 等でサービスを起動
- 認証情報が間違っている: `.env` ファイルまたは環境変数を確認
- データベースが存在しない: `createdb <db_name>` でデータベースを作成

### テストデータが残っている場合

```sh {"name":"<prefix>-force-cleanup"}
# 強制クリーンアップ
npm run test:cleanup --force

# データベース再構築
DROP DATABASE test_db;
CREATE DATABASE test_db;
npm run migrate
```

## ベストプラクティス

### 1. Setup と Cleanup を必ず実装

テストの前後で環境をクリーンな状態に保つ：

```sh {"name":"<prefix>-setup-clean-state"}
# データベースリセット
npm run db:reset

# テストデータ投入
npm run db:seed
```

```sh {"name":"<prefix>-cleanup-after-test"}
# テストデータ削除
npm run db:cleanup

# サーバー停止
pkill -f "npm run dev"
```

### 2. 冪等性を確保

同じテストを何度実行しても同じ結果になるようにする：

```sh {"name":"<prefix>-idempotent-test"}
# 既存データを削除してから作成
curl -X DELETE http://localhost:3000/api/users/test@example.com
curl -X POST http://localhost:3000/api/users \
  -d '{"email": "test@example.com", ...}'
```

### 3. 一括実行

`runme run --all` で verify.md 内のすべてのテストを一括実行できます：

```bash
runme run --all --filename verify.md
```

特定のテストをスキップしたい場合は `excludeFromRunAll` 属性を使用：

```markdown
```sh {"excludeFromRunAll":"true","name":"<prefix>-test-optional"}
# このテストは --all では実行されない
```
```

### 4. タイムアウトの設定

長時間かかる操作にはタイムアウトを設定：

```sh {"name":"<prefix>-test-with-timeout"}
# 10秒でタイムアウト
timeout 10s curl -X GET http://localhost:3000/api/slow-endpoint

# または、Pythonで
python -c "
import requests
response = requests.get('http://localhost:3000/api/slow-endpoint', timeout=10)
print(response.json())
"
```

## よくある質問

**Q: ユニットテストとverify.mdはどう使い分けるか？**

A:
- **ユニットテスト**: ビジネスロジック、純粋関数、バリデーション（外部依存なし）
- **verify.md**: End-to-Endフロー、外部依存（DB、API）、複数コンポーネント結合

**Q: verify.mdのテストが失敗した場合、ユニットテストは書かなくていいのか？**

A: いいえ。verify.mdの失敗は「統合テストレベルでの問題」を示します。その後、ユニットテストを書いて個別のロジックを検証します。

**Q: CI/CDでverify.mdを実行するには？**

A:
```yaml
# GitHub Actions例
- name: Run integration tests
  run: |
    runme run --all --filename verify.md
```

**Q: verify.mdのテストはどれくらいの時間で完了すべきか？**

A: 理想は1-5分以内。それ以上かかる場合、テストを分割することを検討します。

**Q: verify.mdのテストが不安定（flaky）な場合は？**

A:
- タイミング問題: `sleep` や `wait-for-it` で待機時間を追加
- テストデータの競合: 各テストで一意のデータを使用
- 外部サービス依存: モックサーバーを使用

## 参考リンク

- [Runme.dev公式ドキュメント](https://docs.runme.dev/)
- [Runme CLI Reference](https://docs.runme.dev/configuration/cli-reference)
- [Runme by Example](https://docs.runme.dev/getting-started/runbyexample)
