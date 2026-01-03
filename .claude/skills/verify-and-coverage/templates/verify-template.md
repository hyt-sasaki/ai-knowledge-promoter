# Verification: [機能名]

このファイルは、実装した機能の受け入れテスト（統合テスト/E2Eテスト）をRunme.dev形式で記述します。

## 使い方

1. このテンプレートを `openspec/changes/<change-id>/verify.md` にコピー
2. `[機能名]`、`[エンドポイント]`、`[期待値]` を実際の値に置き換え
3. 各コードブロックの `{"name":"<prefix>-..."}` 属性を適切な名前に変更
   - **重要**: `<prefix>`には`change-id`または機能名を使用（例: `add-auth-test-create-user`）
   - これによりプロジェクト内でコマンド名がユニークになります
4. `README.md`を作成し、一括実行コマンドを記述
5. `runme run --all --filename verify.md` ですべてのテストを実行

詳細な実装ガイドは [verify-guide.md](../references/verify-guide.md) を参照してください。

---

## Setup

```sh {"name":"<prefix>-setup-database"}
# データベースマイグレーション実行
npm run migrate
```

```sh {"name":"<prefix>-start-server"}
# アプリケーション起動（バックグラウンド）
npm run dev &
sleep 3
```

```sh {"name":"<prefix>-setup-test-data"}
# テストデータ作成（必要な場合）
curl -X POST http://localhost:3000/api/test/setup
```

---

## Normal Path（正常系）

```sh {"name":"<prefix>-test-create-resource"}
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

```sh {"name":"<prefix>-test-get-resource"}
# リソース取得テスト
RESOURCE_ID=$(curl -s -X POST http://localhost:3000/api/[エンドポイント] ... | jq -r '.id')
curl -X GET http://localhost:3000/api/[エンドポイント]/$RESOURCE_ID

# 期待値:
# ステータスコード: 200
# レスポンス: {"id": "...", "key1": "value1", ...}
```

```sh {"name":"<prefix>-test-update-resource"}
# リソース更新テスト
RESOURCE_ID=$(curl -s -X POST ... | jq -r '.id')
curl -X PUT http://localhost:3000/api/[エンドポイント]/$RESOURCE_ID \
  -H "Content-Type: application/json" \
  -d '{"key1": "updated_value"}'

# 期待値:
# ステータスコード: 200
# レスポンス: {"id": "...", "key1": "updated_value", ...}
```

```sh {"name":"<prefix>-test-list-resources"}
# リソース一覧取得テスト
curl -X GET http://localhost:3000/api/[エンドポイント]

# 期待値:
# ステータスコード: 200
# レスポンス: [{"id": "...", ...}, ...]
```

```sh {"name":"<prefix>-test-delete-resource"}
# リソース削除テスト
RESOURCE_ID=$(curl -s -X POST ... | jq -r '.id')
curl -X DELETE http://localhost:3000/api/[エンドポイント]/$RESOURCE_ID

# 期待値:
# ステータスコード: 204
```

---

## Edge Cases（異常系）

```sh {"name":"<prefix>-test-invalid-input"}
# 無効な入力テスト
curl -X POST http://localhost:3000/api/[エンドポイント] \
  -H "Content-Type: application/json" \
  -d '{"email": "invalid-format"}'

# 期待値:
# ステータスコード: 400
# レスポンス: {"error": "validation_failed", "message": "..."}
```

```sh {"name":"<prefix>-test-missing-required-field"}
# 必須フィールド欠落テスト
curl -X POST http://localhost:3000/api/[エンドポイント] \
  -H "Content-Type: application/json" \
  -d '{"key1": "value1"}'

# 期待値:
# ステータスコード: 400
# レスポンス: {"error": "validation_failed", "message": "Missing required field"}
```

```sh {"name":"<prefix>-test-not-found"}
# 存在しないリソース取得テスト
curl -X GET http://localhost:3000/api/[エンドポイント]/non-existent-id

# 期待値:
# ステータスコード: 404
# レスポンス: {"error": "not_found"}
```

```sh {"name":"<prefix>-test-unauthorized-access"}
# 未認証アクセステスト
curl -X GET http://localhost:3000/api/protected/resource

# 期待値:
# ステータスコード: 401
# レスポンス: {"error": "unauthorized"}
```

---

## Cleanup

```sh {"name":"<prefix>-cleanup-test-data"}
# テストデータクリーンアップ
npm run test:cleanup
```

```sh {"name":"<prefix>-stop-server"}
# サーバー停止
pkill -f "npm run dev"
```

---

## Auto-Test Targets（自動テストでカバーすべき内容）

> このセクションは、ユニットテストでカバーすべきシナリオを明示します。
> verify.md（統合テスト）ではなく、各言語のテストフレームワークで実装します。

### Primary Test Cases（主要ケース）

> spec.mdのGIVEN/WHEN/THENから抽出した主要ケース。

| Requirement | Scenario | WHEN/THEN | Priority | Reason |
|-------------|----------|-----------|----------|--------|
| [要件名] | [シナリオ名] | [条件 → 結果] | P1 | 正常系コアパス |
| [要件名] | [シナリオ名] | [条件 → 結果] | P2 | バリデーション |

### Test Selection Constraints（選定制約）

Step 4でテストケースを追加する際は、以下の制約を適用して過剰生成を防止します。

- [ ] **C1網羅**: 分岐網羅を満たす最小限のケースを抽出
- [ ] **同値分割**: 冗長なテストケースを統合（例: `""`, `None`, `"   "` → 代表値1件）
- [ ] **優先順位**: P1正常系1件 + P2境界値2件以内に絞る
- [ ] **インターフェース集中**: 外部から見た振る舞いのみテスト（内部実装詳細は除外）

### Expected Test Files

- `tests/test_xxx.py` - [テスト対象の説明]

### Coverage Expectations

- **ビジネスロジック・純粋関数**: ユニットテストで80%以上カバー
- **verify.md**: End-to-Endフローのみ（外部依存・結合）
- **テストピラミッド**: ユニットテスト >> 統合テスト（verify.md）
