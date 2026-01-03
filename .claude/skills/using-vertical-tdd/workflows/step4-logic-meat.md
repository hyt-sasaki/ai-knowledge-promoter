# Step 4: Logic Meat

## 目的

スケルトンの内部を本物のロジックに置き換えます。ユニットTDDサイクル（Red-Green-Refactor）を使用して、各関数・メソッドを実装します。

**前提条件**: [Step 2](step2-runbook-red.md) でverify.mdの「Auto-Test Targets」セクションに主要テストケースが記載済みであること。

## テストケース選定制約（過剰生成防止）

テストケースを作成する際は、以下の制約を適用して過剰なテスト生成を防止します。

### 制約1: C1（分岐網羅）を満たす最小限

すべての分岐（if/else、switch/case等）を少なくとも1回は通過するケースのみを選定します。同じ分岐を複数回通過するテストは冗長として削除します。

**例**:
```python
def validate_content(content: str) -> bool:
    if not content:           # Branch 1: 空チェック
        return False
    if len(content) > 10000:  # Branch 2: 長さチェック
        return False
    return True               # Branch 3: 正常
```

**最小限のテストケース（3件）**:
1. `content=""` → Branch 1 → False
2. `content="x" * 10001` → Branch 2 → False
3. `content="valid"` → Branch 3 → True

### 制約2: 同値分割法による冗長排除

同じ結果をもたらす入力は1つの代表値のみテストします。

**例**:
```
「空」の同値クラス:
- "" (空文字列)
- None
- "   " (空白のみ)

→ 代表値: "" のみテスト（他は冗長）
```

### 制約3: 優先順位による絞り込み

| 優先度 | 種類 | 上限 | 例 |
|--------|------|------|-----|
| P1 | 正常系（コアパス） | 1件 | 保存成功 |
| P2 | 致命的境界値 | 2件 | 最大長超過、空入力 |
| P3 | ビジネス例外 | 1件 | 重複エラー |

**原則**: P1正常系1件 + P2境界値2件 + P3例外1件 = 最大4件程度

### 制約4: インターフェースの振る舞いに集中

内部実装の詳細ではなく、外部から見た入出力をテストします。プライベートメソッドの直接テストは避けます。

**NG例**（内部実装詳細）:
```python
def test_internal_hash_algorithm():
    assert _calculate_hash("data") == "expected_hash"
```

**OK例**（振る舞い）:
```python
def test_password_is_not_stored_in_plaintext():
    user = create_user(password="secret123")
    assert user.hashed_password != "secret123"
```

## テスト戦略：テストピラミッド

### テストの役割分担

```
        /\
       /  \  E2E/統合テスト（verify.md / Runbook）
      /----\   - 外部リソース依存（DB、API、ファイルシステム）
     /      \  - 複数コンポーネント結合
    /--------\ - システム全体の動作確認
   /          \
  /------------\ ユニットテスト
 /--------------\  - ビジネスロジック
/----------------\ - 純粋関数、クラスメソッド
                   - 外部依存なし（モック使用）
```

### ユニットテスト優先原則

✅ **ユニットテストでカバーすべきもの**:
- ビジネスロジック（計算、変換、検証）
- 純粋関数（入力→出力、副作用なし）
- クラスメソッド（外部依存をモック）
- エッジケース、バリデーション
- エラーハンドリング

✅ **verify.md（Runbook）でカバーすべきもの**:
- End-to-Endフロー（UI/CLI → API → DB）
- 外部リソース依存（実際のDB接続、ファイルI/O）
- 複数コンポーネント結合（認証 → API → DB → レスポンス）
- システム全体の動作確認

**原則**: 可能な限りユニットテストで検証し、外部依存や結合コストが高いものだけverify.mdで確認します。

## テストケース合意フェーズ（assert Falseパターン）

### 目的

テスト実装前にテストケース（テスト関数名）をAIとユーザーで合意し、過剰なテスト生成を防止します。

### ワークフロー

```
┌─────────────────────────────────────────────────────────────────┐
│ Phase 1: テストケース名の提案                                    │
├─────────────────────────────────────────────────────────────────┤
│ 1. Auto-Test Targets（Step 2で洗い出し済み）を確認               │
│ 2. 追加の異常系ケースを洗い出し                                  │
│ 3. テスト選定制約を適用してケースを絞り込み                      │
│ 4. `assert False` のみのテスト関数を作成                         │
│ 5. ユーザーに確認を依頼                                          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ Phase 2: ユーザー確認                                            │
├─────────────────────────────────────────────────────────────────┤
│ ユーザーが以下を確認：                                           │
│ - テストケース名は適切か？                                       │
│ - 過不足はないか？                                               │
│ - 優先順位は正しいか？                                           │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ Phase 3: 合意後のテスト実装                                      │
├─────────────────────────────────────────────────────────────────┤
│ 1. 合意したテストケースを1件ずつRED-GREEN-REFACTOR              │
│ 2. `assert False` を本物のアサーションに置き換え                 │
└─────────────────────────────────────────────────────────────────┘
```

### assert Falseパターンの例

#### Phase 1: テストケース名の提案

```python
# tests/test_save_knowledge.py
"""Save Knowledge ツールのユニットテスト。

テストケース一覧（合意待ち）:
- test_save_with_content_returns_id: content提供で保存成功
- test_save_empty_content_raises_error: 空contentでバリデーションエラー
- test_save_auto_generates_title: タイトル未指定時の自動生成
"""

import pytest


class TestSaveKnowledge:
    """Save Knowledge ツールのテスト。"""

    def test_save_with_content_returns_id(self):
        """正常系: content提供で保存成功。

        spec.md Scenario: ナレッジ保存成功
        """
        assert False  # TODO: 合意後に実装

    def test_save_empty_content_raises_error(self):
        """異常系: 空contentでバリデーションエラー。

        spec.md Scenario: ナレッジ保存失敗（必須パラメータ不足）
        """
        assert False  # TODO: 合意後に実装

    def test_save_auto_generates_title(self):
        """正常系: タイトル未指定時の自動生成。

        追加理由: UI/UXとして必要な機能
        """
        assert False  # TODO: 合意後に実装
```

#### ユーザーへの確認メッセージ

```markdown
## テストケース合意確認

以下のテストケースを提案します。過不足があればご指摘ください。

### tests/test_save_knowledge.py

| No | テスト関数名 | カテゴリ | 説明 | 根拠 |
|----|-------------|---------|------|------|
| 1 | `test_save_with_content_returns_id` | Primary | 正常系: 保存成功 | spec.md Scenario 1 |
| 2 | `test_save_empty_content_raises_error` | Primary | 異常系: 空content | spec.md Scenario 2 |
| 3 | `test_save_auto_generates_title` | Secondary | 正常系: タイトル自動生成 | 実装仕様 |

### 選定制約の適用結果

| 制約 | 適用結果 |
|------|---------|
| C1網羅 | 3ケースで主要分岐カバー |
| 同値分割 | 空は代表値1件に統合 |
| 優先順位 | Primary 2件 + Secondary 1件 |
| インターフェース集中 | 入出力のみテスト |

合意いただけますか？修正・追加・削除のご要望があればお知らせください。
```

#### Phase 3: 合意後の実装

```python
# assert False を本物のアサーションに置き換え
def test_save_with_content_returns_id(self):
    """正常系: content提供で保存成功。"""
    self.mock_repository.save.return_value = Knowledge(
        id="generated-id",
        title="Test Title",
        content="Test content",
    )

    result = self.save_knowledge(
        title="Test Title",
        content="Test content",
    )

    assert result["status"] == "saved"
    assert result["id"] == "generated-id"
```

### テストケース合意チェックリスト

```
テストケース合意:
- [ ] Auto-Test Targets（Step 2）を確認
- [ ] 追加の異常系ケースを洗い出し
- [ ] テスト選定制約を適用
- [ ] `assert False` テストファイル作成
- [ ] ユーザーに確認を依頼
- [ ] 合意を取得
- [ ] 合意後に本実装を開始
```

## Step 2との連携ガイドライン

### 入力

1. **Auto-Test Targets（Step 2で洗い出し済み）**
   - verify.mdの「Auto-Test Targets」セクションを参照
   - spec.mdのGIVEN/WHEN/THENから抽出済みの主要ケース

2. **追加で洗い出す異常系**
   - spec.mdに明記されていないが、実装上必要な異常系
   - ただし選定制約を適用して最小限に

### 追加ケース洗い出しの観点

| 観点 | 例 | 追加基準 |
|------|-----|---------|
| 型エラー | None渡し、型不一致 | 動的型付け言語の場合のみ |
| 境界値 | 最大長+1、0、負数 | 仕様に明記がない致命的なもののみ |
| 状態依存 | 初期化前呼び出し | クラスメソッドの場合のみ |
| 並行性 | 競合状態 | 並行処理が仕様の場合のみ |

### 追加ケースの記録形式

verify.mdまたはテストファイル内で追加ケースを記録します：

```markdown
### Additional Test Cases（Step 4で追加）

> spec.mdに明記されていないが、実装上必要な異常系。

| テスト関数名 | 説明 | 追加理由 |
|-------------|------|---------|
| `test_save_whitespace_content_raises_error` | 空白のみでバリデーションエラー | 同値分割の境界 |
| `test_save_none_tags_defaults_to_empty_list` | None tagsはデフォルト空リスト | 防御的プログラミング |
```

## ユニットTDDサイクル

各関数・メソッドごとに以下のサイクルを繰り返します：

**注**: 以下のコード例はPythonを使用していますが、この方法論は言語非依存です。Node.js、Go、Rust、Java等でも同様のサイクルを適用できます。各言語のテストフレームワーク（Jest、Go testing、RSpec等）で同じパターンを使用してください。

### 1. Red: テスト先行

**コンセプト**: 実装前にテストを書き、失敗（RED）を確認します。

```python
# 例: Python (pytest)
# tests/test_users.py
def test_create_user_hashes_password():
    """パスワードがbcryptでハッシュ化されることを検証"""
    user = create_user_in_db(email="test@example.com", password="SecurePass123")

    # パスワードがそのまま保存されていないことを確認
    assert user.hashed_password != "SecurePass123"
    # bcryptハッシュの形式を確認（$2b$で始まる）
    assert user.hashed_password.startswith("$2b$")
```

**実行結果（RED）**:
```
FAILED tests/test_users.py::test_create_user_hashes_password
AttributeError: 'User' object has no attribute 'hashed_password'
```

### 2. Green: テストをパスさせる最小実装

**コンセプト**: テストをパスさせる最小限のコードを書きます。

```python
# 例: Python (FastAPI + bcrypt)
# lib/users.py
import bcrypt

def create_user_in_db(email: str, password: str) -> User:
    # パスワードをbcryptでハッシュ化
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    # ユーザーをDBに挿入（スケルトンのハードコードを本物に置き換え）
    user = User(
        id=generate_uuid(),  # ハードコード "dummy-123" を実装に置き換え
        email=email,
        hashed_password=hashed.decode(),
        created_at=datetime.utcnow()  # 固定値を実時刻に置き換え
    )
    db.add(user)
    db.commit()
    return user
```

**実行結果（GREEN）**:
```
PASSED tests/test_users.py::test_create_user_hashes_password
```

### 3. Refactor: リファクタリング

**コンセプト**: テストがGREENを維持しながら、コードを改善します（重複削減、関数抽出、可読性向上）。

```python
# 例: Python（リファクタリング後）
# lib/users.py
def hash_password(password: str) -> str:
    """パスワードをbcryptでハッシュ化"""
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    return hashed.decode()

def create_user_in_db(email: str, password: str) -> User:
    user = User(
        id=generate_uuid(),
        email=email,
        hashed_password=hash_password(password),  # 関数に抽出
        created_at=datetime.utcnow()
    )
    db.add(user)
    db.commit()
    return user
```

**実行結果（GREEN維持）**:
```
PASSED tests/test_users.py::test_create_user_hashes_password
```

## スケルトンからロジックへの置き換え手順

### 1. ハードコード部分を特定

スケルトン実装を確認し、ハードコード部分をリストアップ：

```python
# Before（スケルトン）
@app.post("/api/users", response_model=UserResponse)
def create_user(user: UserCreate):
    return UserResponse(
        id="dummy-user-123",  # ← ハードコード1
        email=user.email,
        created_at="2025-12-31T00:00:00Z"  # ← ハードコード2
    )
```

### 2. ユニットテストを書く（RED）

```python
# tests/test_users.py
def test_create_user_generates_unique_id():
    """ユーザー作成時に一意なIDが生成されることを検証"""
    user1 = create_user_in_db(email="user1@example.com", password="pass1")
    user2 = create_user_in_db(email="user2@example.com", password="pass2")

    assert user1.id != user2.id  # ← このテストがREDになる
```

### 3. 本実装に置き換え（GREEN）

```python
# After（本実装）
import uuid
from datetime import datetime

@app.post("/api/users", response_model=UserResponse)
def create_user(user: UserCreate):
    # スケルトンのハードコードを本実装に置き換え
    db_user = create_user_in_db(email=user.email, password=user.password)

    return UserResponse(
        id=str(db_user.id),  # UUID生成
        email=db_user.email,
        created_at=db_user.created_at.isoformat()  # 実時刻
    )

def create_user_in_db(email: str, password: str) -> User:
    user = User(
        id=uuid.uuid4(),  # ハードコード "dummy-123" → UUID生成
        email=email,
        hashed_password=hash_password(password),
        created_at=datetime.utcnow()  # 固定値 → 実時刻
    )
    db.add(user)
    db.commit()
    return user
```

### 4. リファクタリング

コードの重複を削減、関数を抽出、型を厳密化：

```python
# リファクタリング後
from typing import Optional

def get_user_by_email(email: str) -> Optional[User]:
    """メールアドレスでユーザーを検索"""
    return db.query(User).filter(User.email == email).first()

def create_user_in_db(email: str, password: str) -> User:
    # メールアドレス重複チェック
    existing_user = get_user_by_email(email)
    if existing_user:
        raise ValueError("Email already registered")

    user = User(
        id=uuid.uuid4(),
        email=email,
        hashed_password=hash_password(password),
        created_at=datetime.utcnow()
    )
    db.add(user)
    db.commit()
    return user
```

## 置き換え対象の優先順位

### Phase 1: コア機能

1. **ID生成**: ハードコード → UUID生成
2. **タイムスタンプ**: 固定値 → 実時刻
3. **データベース操作**: モック → 実際のCRUD

### Phase 2: バリデーション

4. **入力検証**: 最小限 → 厳密な検証（email形式、パスワード強度等）
5. **重複チェック**: なし → 一意性制約の検証

### Phase 3: エラーハンドリング

6. **例外処理**: 基本的なもの → 詳細なエラーメッセージ
7. **ロールバック**: なし → トランザクション管理

## フィードバックループ

各機能の実装後、以下を実行：

### ユニットテスト実行

**言語別テストフレームワーク例**:

```bash
# Python (pytest)
pytest tests/
pytest --cov=lib --cov-report=html  # カバレッジ確認

# Node.js (Jest)
npm test
npm test -- --coverage  # カバレッジ確認

# Go
go test ./...
go test -cover ./...  # カバレッジ確認

# Rust
cargo test
cargo tarpaulin  # カバレッジ確認（tarpaulin使用）
```

### verify.md確認（統合テスト）

```bash
# verify.mdですべてGREENであることを確認
runme run verify-all

# 期待: すべてのテストがパス（スケルトン時と同じ）
# 違い: 内部がハードコードではなく、本物のロジックに置き換わっている
```

**重要**: verify.mdの結果は変わらないはず。内部実装が変わっただけで、外部から見た挙動は同じです。

### テストピラミッドの確認

- ✅ **ユニットテスト**: ビジネスロジック、純粋関数、バリデーションをカバー
- ✅ **verify.md（統合テスト）**: End-to-Endフロー、外部リソース依存をカバー
- ✅ **カバレッジ**: ユニットテストで80%以上を目標（外部依存を除く）

## 実装チェックリスト

```
ロジック実装進捗:
- [ ] ID生成ロジック実装（ユニットテスト → GREEN）
- [ ] タイムスタンプ実装（ユニットテスト → GREEN）
- [ ] データベースCRUD実装（ユニットテスト → GREEN）
- [ ] パスワードハッシュ化実装（ユニットテスト → GREEN）
- [ ] 入力検証実装（ユニットテスト → GREEN）
- [ ] 重複チェック実装（ユニットテスト → GREEN）
- [ ] エラーハンドリング実装（ユニットテスト → GREEN）
- [ ] すべてのユニットテストがパス
- [ ] カバレッジ80%以上（ビジネスロジック・純粋関数を対象）
- [ ] verify.mdがすべてGREEN（統合テスト、End-to-Endフロー確認）
- [ ] テストピラミッド確認（ユニット >> 統合）
```

## PR #2 作成

### PR情報

- **ブランチ名**: `logic/<change-id>`
- **タイトル**: `[Logic] <feature-name>`
- **ラベル**: `enhancement`, `ready-for-review`

### PR本文テンプレート

```markdown
## Logic Implementation: <feature-name>

This PR replaces hardcoded skeleton with real business logic.

### What's Included

- ✅ Real database operations (CRUD)
- ✅ Password hashing (bcrypt)
- ✅ Input validation
- ✅ Error handling
- ✅ Unit tests (coverage: XX%)

### Changes from Skeleton

| Before (Skeleton) | After (Logic) |
|-------------------|---------------|
| Hardcoded ID: `"dummy-123"` | UUID generation: `uuid.uuid4()` |
| Fixed timestamp | Real timestamp: `datetime.utcnow()` |
| No DB operations | SQLAlchemy CRUD |
| No validation | Email format, password strength |

### Unit Tests

All unit tests pass:

\`\`\`bash
# 例: Python (pytest)
pytest tests/
# PASSED tests/test_users.py::test_create_user_generates_unique_id
# PASSED tests/test_users.py::test_create_user_hashes_password
# PASSED tests/test_users.py::test_create_user_validates_email
# ... (total: XX tests)

# 例: Node.js (Jest)
npm test
# PASS tests/users.test.js
#   ✓ generates unique ID (10ms)
#   ✓ hashes password (15ms)
#   ✓ validates email format (5ms)
# ... (total: XX tests)
\`\`\`

**Coverage**: XX% (target: 80%+ for business logic and pure functions)

### Integration Tests (verify.md)

verify.md still passes (GREEN):

\`\`\`bash
runme run verify-all
# ✅✅✅ All tests GREEN ✅✅✅
\`\`\`

### Test Pyramid Confirmation

- ✅ **Unit tests**: Cover business logic, pure functions, validations
- ✅ **Integration tests**: Cover End-to-End flows, external dependencies
- ✅ **Ratio**: Unit tests >> Integration tests (following test pyramid)

### Related

- PR #2: Skeleton implementation (merged)
- OpenSpec proposal: `openspec/changes/<change-id>/proposal.md`

### Next Steps

- [ ] PR #3: Merge logic (this PR)
- [ ] PR #N: Archive and release
```

### PR作成コマンド

```bash
# ブランチ作成
git checkout -b logic/<change-id>

# ファイル追加
git add lib/ tests/
git commit -m "$(cat <<'EOF'
[Logic] <feature-name>

Replace skeleton hardcoded logic with real implementation.
- UUID generation
- bcrypt password hashing
- Database CRUD operations
- Input validation
- Error handling

Unit tests: XX tests, coverage: XX%
verify.md: ✅✅✅ All tests GREEN

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"

# プッシュ
git push -u origin logic/<change-id>

# PR作成
gh pr create --title "[Logic] <feature-name>" --body "$(cat PR_BODY.md)"
```

## PR #3レビューとマージ

### レビューポイント

- [ ] すべてのハードコードが本実装に置き換わっている
- [ ] ユニットテストがすべてパス
- [ ] カバレッジが80%以上
- [ ] verify.mdがすべてGREEN（統合テスト）
- [ ] エラーハンドリングが適切
- [ ] コードがリファクタリングされている

### マージ後

```bash
git checkout main
git pull origin main
```

## tasks.md更新

PR #3マージ後、tasks.mdを更新：

```markdown
## 2. 実装フェーズ
- [x] verify.md作成
- [x] REDステータス確認
- [x] スケルトン実装
- [x] PR #2作成・マージ
- [x] ロジック実装
- [x] ユニットテスト実装
- [x] PR #3作成・マージ  ← 完了マーク
```

## チェックリスト

Step 4完了前に確認：

- [ ] すべてのハードコードを本実装に置き換え済み
- [ ] ユニットテストがすべてパス（pytest）
- [ ] カバレッジ80%以上
- [ ] verify.mdがすべてGREEN（runme run verify-all）
- [ ] PR #3作成・レビュー・マージ済み
- [ ] tasks.mdを更新済み

## コミット戦略

このステップでのコミットポイント：

**各機能のユニットテスト完了後（小さく頻繁に）**
```bash
git add tests/ lib/
git commit -m "feat: implement <specific-feature> logic"
```

**ロジック実装完了・verify.md再確認後**
```bash
git commit -m "feat: complete logic implementation for <feature-name>"
```

詳細は [commit-strategy.md](commit-strategy.md) を参照。

## 次のステップ

PR #3マージ後 → **Step 5: Archive & Release**

全テストとverify.mdの最終検証を行い、OpenSpecアーカイブとフィーチャーフラグ有効化を実施します。

## よくある質問

**Q: verify.mdの結果がスケルトン時と変わらないのは正しいのか？**

A: はい。verify.mdは外部から見た挙動をテストします。内部がハードコードから本実装に変わっても、APIレスポンスは同じ形式なので、verify.mdの結果は変わりません。

**Q: ユニットテストとverify.md（統合テスト）の違いは？**

A:
- **ユニットテスト**: ビジネスロジック、純粋関数、バリデーションを対象。外部依存をモック化。高速で大量のテストケースを実行。
- **verify.md（統合テスト）**: End-to-Endフロー、実際の外部リソース（DB、API、ファイルシステム）を対象。システム全体の動作確認。
- **テストピラミッド**: ユニットテストを大量に、統合テストを少数に保つことで、高速かつ信頼性の高いテストスイートを構築します。

**Q: すべてのロジックをユニットテストでカバーすべきか？**

A: いいえ。外部リソース依存（DB接続、ファイルI/O、外部API）や複数コンポーネント結合は、verify.mdで確認します。ビジネスロジック、純粋関数、バリデーションはユニットテストでカバーします。

**Q: カバレッジ80%未満の場合はマージできないのか？**

A: プロジェクトの基準に従います。一般的には80%を目標としますが、外部依存が多い場合はカバレッジが低くなることもあります。統合テスト（verify.md）がGREENであれば許容される場合もあります。

**Q: ユニットテストが失敗した場合は？**

A: 失敗したテストを修正するまでPR #2を作成しません。Red-Green-Refactorサイクルを繰り返し、すべてGREENにします。

**Q: リファクタリングはどこまでやるべきか？**

A: 以下を基準にします：
- 重複コードの削減
- 関数の単一責任原則
- 読みやすさの向上
ただし、過度な抽象化は避けます。

**Q: 他の言語（Node.js、Go、Rust等）でも同じ方法論を使えるか？**

A: はい。Red-Green-Refactorサイクル、テストピラミッド、verify.md（統合テスト）は言語非依存です。各言語のテストフレームワーク（Jest、Go testing、RSpec等）で同じパターンを適用できます。
