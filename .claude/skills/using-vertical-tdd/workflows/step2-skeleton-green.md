# Step 2: Skeleton Green

## 目的

verify.mdがパスする最小限の実装（ハードコードやモック可）でシステム疎通を証明します。

## スケルトン実装の原則

### ✅ DO（実装すべきこと）

- **疎通優先**: UIからDBまで貫通させる（End-to-End）
- **ハードコード可**: `return {"status": "ok", "id": "dummy-123"}` で十分
- **モック可**: 実データ不要、ダミーレスポンスでOK
- **最小限**: verify.mdをパスする最低限のコードのみ
- **型定義**: インターフェースとデータ型は正確に定義
- **フィーチャーフラグ**: 環境変数で機能ON/OFF切り替え可能に

### ❌ DON'T（実装しないこと）

- **ビジネスロジック禁止**: 計算、検証、変換ロジックは書かない
- **データベースクエリ禁止**: 実際のDB操作は行わない（モックで代用）
- **外部API呼び出し禁止**: 実際のHTTPリクエストは行わない
- **エラーハンドリング複雑化禁止**: 最小限の例外処理のみ
- **最適化禁止**: パフォーマンスチューニングは後回し

## フィーチャーフラグパターン

スケルトン実装はフィーチャーフラグで制御し、デフォルトはOFFにします。

### 環境変数での制御

```python
import os

FEATURE_USER_AUTH_ENABLED = os.getenv("FEATURE_USER_AUTH_ENABLED", "false") == "true"

@app.post("/api/users")
def create_user(user: UserCreate):
    if not FEATURE_USER_AUTH_ENABLED:
        raise HTTPException(status_code=503, detail="Feature not available")

    # スケルトン実装（ハードコード）
    return {
        "id": "dummy-user-123",
        "email": user.email,
        "created_at": "2025-12-31T00:00:00Z"
    }
```

### .envファイル

```bash
# 開発環境では有効化
FEATURE_USER_AUTH_ENABLED=true

# 本番環境ではデフォルトでfalse（環境変数未設定）
```

## スケルトン実装例

### 例1: FastAPI ユーザー作成エンドポイント

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os

app = FastAPI()

FEATURE_USER_AUTH_ENABLED = os.getenv("FEATURE_USER_AUTH_ENABLED", "false") == "true"

class UserCreate(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    created_at: str

@app.post("/api/users", response_model=UserResponse)
def create_user(user: UserCreate):
    if not FEATURE_USER_AUTH_ENABLED:
        raise HTTPException(status_code=503, detail="Feature not available")

    # スケルトン実装：ハードコードレスポンス
    # ビジネスロジック、DB操作、バリデーションは一切なし
    return UserResponse(
        id="dummy-user-123",
        email=user.email,  # リクエストの値をそのまま返す
        created_at="2025-12-31T00:00:00Z"  # 固定値
    )

@app.get("/api/users/{user_id}", response_model=UserResponse)
def get_user(user_id: str):
    if not FEATURE_USER_AUTH_ENABLED:
        raise HTTPException(status_code=503, detail="Feature not available")

    # スケルトン実装：常に同じダミーデータを返す
    return UserResponse(
        id=user_id,  # パスパラメータをそのまま返す
        email="dummy@example.com",  # 固定値
        created_at="2025-12-31T00:00:00Z"
    )
```

### 例2: Next.js App Router Server Component

```tsx
// app/users/page.tsx
import { getUserList } from '@/lib/users'

export default async function UsersPage() {
  const users = await getUserList()

  return (
    <div>
      <h1>Users</h1>
      <ul>
        {users.map((user) => (
          <li key={user.id}>{user.email}</li>
        ))}
      </ul>
    </div>
  )
}
```

```typescript
// lib/users.ts
export async function getUserList() {
  // スケルトン実装：ハードコードされたダミーデータ
  // 実際のfetch()やDBクエリは行わない
  return [
    { id: 'dummy-1', email: 'user1@example.com' },
    { id: 'dummy-2', email: 'user2@example.com' },
  ]
}
```

## verify.mdでのGREEN確認

スケルトン実装完了後、verify.mdを実行してGREENを確認します。

### 実行手順

```bash
cd openspec/changes/<change-id>/

# フィーチャーフラグを有効化
export FEATURE_USER_AUTH_ENABLED=true

# verify-allで一括テスト
runme run verify-all
```

### 期待される結果（GREEN）

✅ setup-database: 成功
✅ start-server: 成功
✅ test-create-user: 成功（ハードコードレスポンスが返る）
✅ test-get-user: 成功（ダミーデータが返る）
✅ test-duplicate-email: 成功（エラーレスポンスはハードコード可）
✅ cleanup-test-data: 成功

**GREENの例**:

```
$ runme run test-create-user
{"id": "dummy-user-123", "email": "test@example.com", "created_at": "2025-12-31T00:00:00Z"}
✅ test-create-user passed

$ runme run verify-all
✅ setup-database passed
✅ start-server passed
✅ test-create-user passed
✅ test-get-user passed
✅ test-duplicate-email passed
✅ test-invalid-email passed
✅ cleanup-test-data passed
✅ stop-server passed
✅✅✅ All tests GREEN ✅✅✅
```

### Runme TUIでの確認

```bash
runme tui
# すべてのテストを実行し、GREEN（成功）を視覚的に確認
```

## PR #1 作成

### PR情報

- **ブランチ名**: `skeleton/<change-id>`
- **タイトル**: `[Skeleton] <feature-name>`
- **ラベル**: `skeleton`, `work-in-progress`

### PR本文テンプレート

```markdown
## Skeleton Implementation: <feature-name>

This PR implements the skeleton (end-to-end connectivity) for <feature-name>.
Business logic will be implemented in a follow-up PR.

### What's Included

- ✅ API endpoints with hardcoded responses
- ✅ Type definitions and interfaces
- ✅ Feature flag (`FEATURE_<NAME>_ENABLED`)
- ✅ verify.md passes (GREEN)

### What's NOT Included

- ❌ Business logic
- ❌ Database operations
- ❌ Input validation
- ❌ Error handling (beyond basics)

### Verification

See [verify.md](openspec/changes/<change-id>/verify.md) for test scenarios.

All tests pass with `FEATURE_<NAME>_ENABLED=true`:

\`\`\`bash
runme run verify-all
# ✅✅✅ All tests GREEN ✅✅✅
\`\`\`

**Screenshot**:
![verify.md GREEN](link-to-screenshot)

### Feature Flag

Feature is **disabled by default** in production:
- Default: `FEATURE_<NAME>_ENABLED=false`
- To enable: Set `FEATURE_<NAME>_ENABLED=true` in environment

### Related

- OpenSpec proposal: `openspec/changes/<change-id>/proposal.md`
- Design doc: `openspec/changes/<change-id>/design.md` (if exists)

### Next Steps

- [ ] PR #1: Merge skeleton (this PR)
- [ ] PR #2: Implement business logic
- [ ] PR #3: Archive and release
```

### PR作成コマンド

```bash
# ブランチ作成
git checkout -b skeleton/<change-id>

# ファイル追加
git add <skeleton-implementation-files>
git add openspec/changes/<change-id>/verify.md

# コミット
git commit -m "$(cat <<'EOF'
[Skeleton] <feature-name>

Implement end-to-end skeleton with hardcoded responses.
Feature flag: FEATURE_<NAME>_ENABLED (default: false)

verify.md passes: ✅✅✅ All tests GREEN

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"

# プッシュ
git push -u origin skeleton/<change-id>

# PR作成
gh pr create --title "[Skeleton] <feature-name>" --body "$(cat PR_BODY.md)"
```

## PR #1レビューとマージ

### レビューポイント

- [ ] verify.mdがすべてGREEN
- [ ] フィーチャーフラグがデフォルトでfalse
- [ ] ビジネスロジックが含まれていない（ハードコードのみ）
- [ ] 型定義が正確
- [ ] End-to-Endで疎通している

### マージ後

```bash
# mainブランチに戻る
git checkout main
git pull origin main

# tasks.md更新
```

## tasks.md更新

PR #1マージ後、tasks.mdを更新：

```markdown
## 2. 実装フェーズ
- [x] verify.md作成（Runme.dev形式）
- [x] REDステータス確認
- [x] スケルトン実装
- [x] PR #1作成・マージ  ← 完了マーク
- [ ] ロジック実装
```

## チェックリスト

Step 2完了前に確認：

- [ ] スケルトン実装完成（ハードコードのみ）
- [ ] フィーチャーフラグ実装済み
- [ ] `runme run verify-all` でGREEN確認済み
- [ ] verify.md GREENのスクリーンショット取得済み
- [ ] PR #1作成済み
- [ ] PR #1レビュー・マージ済み
- [ ] tasks.mdを更新済み

## 次のステップ

PR #1マージ後 → **Step 3: Logic Meat**

スケルトンの内部を本物のロジックに置き換えます。

## よくある質問

**Q: ハードコードだけで本当にマージして良いのか？**

A: はい。フィーチャーフラグでデフォルトOFFなので、本番環境には影響しません。システム疎通を証明することが目的です。

**Q: Edge Cases（異常系）もハードコードで良いのか？**

A: はい。例えば「重複メールエラー」も `if email == "test@example.com": raise HTTPException(...)` のようなハードコードで十分です。

**Q: データベースマイグレーションは含めるのか？**

A: テーブルスキーマのみ作成します。実際のデータ挿入・取得ロジックはStep 3で実装します。

**Q: verify.mdの一部がまだREDの場合は？**

A: すべてGREENになるまでスケルトンを調整します。部分的なGREENではマージしません。

**Q: フィーチャーフラグの命名規則は？**

A: `FEATURE_<NAME>_ENABLED` の形式。例: `FEATURE_USER_AUTH_ENABLED`, `FEATURE_PAYMENT_ENABLED`
