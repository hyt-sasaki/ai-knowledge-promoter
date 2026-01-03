# Step 2: Runbook & Red

## 目的

Runme.dev形式でverify.mdを作成し、期待する挙動をcURLやCLIコマンドで記述してRED（失敗）を確認します。

## verify.mdの役割（テストピラミッド）

verify.mdは**統合テスト/E2Eテスト**として機能します：

- ✅ **End-to-Endフロー確認**: UI/CLI → API → DB → レスポンス
- ✅ **外部リソース依存**: 実際のDB接続、ファイルI/O、外部API
- ✅ **複数コンポーネント結合**: 認証、API、データベース等の統合動作
- ✅ **システム全体の動作確認**: 本番環境に近い状態でのテスト

**注**: ビジネスロジック、純粋関数、バリデーション等は**ユニットテスト**でカバーします（Step 3で実装）。verify.mdは外部依存や結合コストが高いものに焦点を当てます。

## 配置場所

`openspec/changes/<change-id>/verify.md`

## Runme.devとは

Runme.devは実行可能なマークダウンドキュメントを作成するツールです。verify.mdをそのままテストスクリプトとして実行できます。

### 主な特徴

- **名前付きコードブロック**: 各コマンドに名前を付けて管理
- **複数の実行方法**: CLI、TUI、VS Code拡張機能
- **多言語対応**: Shell、Python、JavaScript、TypeScript等
- **環境変数管理**: .envファイルとの統合

### インストール確認

このプロジェクトでは `mise.toml` でRunme.devを管理しています。miseが自動的にインストールします。

```bash
# インストール確認
runme --version

# 利用可能なコマンド一覧
runme --help
```

## verify.md作成

### テンプレート使用

**verify-and-coverage Skill** のテンプレートを使用します。

詳細は `.claude/skills/verify-and-coverage/` を参照してください。

### 名前付きコードブロックの形式

**重要**: コードブロックに `{"name":"command-name"}` 属性を追加します。

```markdown
```sh {"name":"setup-database"}
npm run migrate
```
```

### verify.md構成

```markdown
# Verification: [機能名]

## Setup

```sh {"name":"setup-database"}
# データベースマイグレーション実行
npm run migrate
```

```sh {"name":"start-server"}
# アプリケーション起動（バックグラウンド）
npm run dev &
sleep 3  # サーバー起動待機
```

## Normal Path（正常系）

```sh {"name":"test-create-user"}
# ユーザー作成テスト
curl -X POST http://localhost:3000/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123"
  }'

# 期待: {"id": "...", "email": "test@example.com", "created_at": "..."}
```

```sh {"name":"test-get-user"}
# ユーザー取得テスト
USER_ID=$(curl -s -X POST http://localhost:3000/api/users ... | jq -r '.id')
curl -X GET http://localhost:3000/api/users/$USER_ID

# 期待: {"id": "...", "email": "test@example.com"}
```

## Edge Cases（異常系）

```sh {"name":"test-duplicate-email"}
# 重複メールアドレステスト
curl -X POST http://localhost:3000/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123"
  }'

# 期待: {"error": "email_already_exists", "message": "Email already registered"}
# ステータスコード: 409
```

```sh {"name":"test-invalid-email"}
# 無効なメールアドレステスト
curl -X POST http://localhost:3000/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "email": "invalid-email",
    "password": "SecurePass123"
  }'

# 期待: {"error": "validation_failed", "message": "Invalid email format"}
# ステータスコード: 400
```

## Cleanup

```sh {"name":"cleanup-test-data"}
# テストデータクリーンアップ
npm run test:cleanup
```

```sh {"name":"stop-server"}
# サーバー停止
pkill -f "npm run dev"
```

## Verify All（一括実行）

```sh {"name":"verify-all"}
# すべてのテストを順次実行
runme run setup-database
runme run start-server
runme run test-create-user
runme run test-get-user
runme run test-duplicate-email
runme run test-invalid-email
runme run cleanup-test-data
runme run stop-server
echo "✅ All tests completed"
```
```

## Runme.dev実行方法

### 方法1: CLI個別実行

```bash
# 利用可能なコマンド一覧を表示
cd openspec/changes/<change-id>/
runme list

# 出力例:
# setup-database
# start-server
# test-create-user
# test-get-user
# test-duplicate-email
# test-invalid-email
# cleanup-test-data
# stop-server
# verify-all

# 個別実行
runme run setup-database
runme run start-server
runme run test-create-user

# verify-all で一括実行
runme run verify-all
```

### 方法2: TUI対話式実行

```bash
# 対話式メニュー起動
runme tui

# 使い方:
# - 矢印キーでコマンド選択
# - Enterキーで実行
# - 実行結果がリアルタイムで表示
# - qキーで終了
```

### 方法3: VS Code拡張機能

1. **拡張機能インストール**
   - VS Codeで「Runme」拡張機能を検索してインストール

2. **verify.mdを開く**
   - 各コードブロックに実行ボタン（▶）が表示される

3. **実行**
   - ▶ボタンをクリックで実行
   - 結果がインライン表示される
   - 複数のコマンドを連続実行可能

## REDステータス確認

### 実行とRED確認

現在の実装状態（未実装またはスケルトン前）でverify.mdを実行し、以下を確認します：

```bash
# verify-allで一括テスト
runme run verify-all
```

**期待される結果（RED）**:

✅ Setup セクションは成功（データベース接続等）
❌ test-create-user は失敗（404 Not Found または 500 Internal Server Error）
❌ test-get-user は失敠（エンドポイント未実装）
❌ Edge Cases も失敗

**REDの例**:

```
$ runme run test-create-user
curl: (22) The requested URL returned error: 404 Not Found
❌ test-create-user failed
```

### REDステータスの記録

tasks.mdまたはverify.mdのコメントに記録：

```markdown
<!-- RED Status (2025-12-31)
- test-create-user: 404 Not Found ✅ (expected)
- test-get-user: 404 Not Found ✅ (expected)
- test-duplicate-email: 404 Not Found ✅ (expected)
-->
```

## フィードバックループチェックリスト

```
verify.md作成進捗:
- [ ] テンプレートをコピー
- [ ] Setup セクション完成（名前付きコードブロック）
- [ ] Normal Path（正常系）テスト記述
- [ ] Edge Cases（異常系）テスト記述
- [ ] Cleanup セクション完成
- [ ] verify-all コマンド作成
- [ ] runme list でコマンド一覧表示確認
- [ ] runme run verify-all でRED確認
- [ ] REDステータスを記録
```

## verify.md作成のベストプラクティス

### 1. 名前付きコードブロックの命名規則

✅ **Good**:
- `setup-database`
- `test-create-user`
- `test-invalid-email`
- `verify-all`

❌ **Bad**:
- `test1`（何のテストか不明）
- `run`（汎用的すぎる）
- `setup`（何をセットアップするか不明）

### 2. 期待値をコメントで明記

```sh {"name":"test-create-user"}
curl -X POST http://localhost:3000/api/users ...

# 期待: {"id": "...", "email": "test@example.com"}
# ステータスコード: 201
```

### 3. 環境変数の使用

```sh {"name":"test-with-auth"}
# 環境変数から認証トークンを読み込み
curl -X GET http://localhost:3000/api/protected \
  -H "Authorization: Bearer $API_TOKEN"
```

### 4. 多言語対応

Shellだけでなく、Python、JavaScriptも使用可能：

```python {"name":"test-create-user-python"}
import requests

response = requests.post(
    "http://localhost:3000/api/users",
    json={"email": "test@example.com", "password": "SecurePass123"}
)
print(response.json())
# 期待: {"id": "...", "email": "test@example.com"}
```

## 中間PRでのテストスキップ戦略

インフラ先行型パターンなど、verify.mdが部分的にREDの状態でPRをマージする場合のテスト管理方法です。

詳細は [pr-splitting-guide.md](../references/pr-splitting-guide.md) を参照してください。

### pytest等のテストフレームワーク

```python
import pytest

@pytest.mark.skip(reason="Implemented in PR #2b: MCP skeleton")
def test_save_knowledge():
    """後続PRで実装予定"""
    pass
```

### runme.dev (verify.md) でのスキップ

コメントアウトと理由コメントを使用します：

```markdown
## Pending Tests（後続PRで実装予定）

<!-- [PENDING] PR #2b: MCP skeleton で実装予定
```sh {"name":"test-save-knowledge"}
curl -X POST http://localhost:8080/mcp/tools/save_knowledge ...
```
-->
```

### verify-all の部分実行

中間PRでは、実装済みのテストのみを実行するよう `verify-all` を調整します：

```markdown
```sh {"name":"verify-all"}
runme run setup
runme run test-health  # このPRで実装済み
runme run cleanup
echo "✅ All implemented tests passed"
echo "⏳ Pending: test-save-knowledge (PR #2b)"
```
```

### tasks.mdにスキップ解除タスクを追記

テストをスキップした場合、**必ず**tasks.mdにスキップ解除タスクを追記して忘れを防ぎます：

```markdown
## 2. 実装フェーズ

### PR #2a: デプロイ基盤
- [x] GCPプロジェクト基盤整備
- [x] Cloud Run + Buildpacks デプロイ検証

### PR #2b: MCPスケルトン
- [ ] test-save-knowledge スキップ解除  ← スキップ解除タスク
- [ ] test-search-knowledge スキップ解除
- [ ] MCPサーバー実装
- [ ] verify.md全テストGREEN確認
```

**重要**: スキップしたテストごとに解除タスクを作成し、後続PRで確実に解除します。

## Auto-Test Targets抽出ガイドライン

verify.md作成時に、spec.mdの各Scenarioをユニットテスト候補として「Auto-Test Targets」セクションに記載します。

### GIVEN/WHEN/THENからの抽出手順

#### Step 1: spec.mdのScenarioをリスト化

spec.mdからGIVEN/WHEN/THEN形式で記述されたScenarioを抽出します。

```markdown
Requirement: Save Knowledge Tool
  Scenario 1: ナレッジ保存成功
    - WHEN: save_knowledge ツールが呼び出される
    - AND: content パラメータが提供される
    - THEN: 成功レスポンスが返される

  Scenario 2: ナレッジ保存失敗（必須パラメータ不足）
    - WHEN: save_knowledge ツールが呼び出される
    - AND: content パラメータが空
    - THEN: エラーレスポンスが返される
```

#### Step 2: 各Scenarioのテストタイプを判定

以下の判定基準で、統合テスト（verify.md）とユニットテスト（Auto-Test Targets）に分類します。

| テストタイプ | 判定基準 | 例 |
|-------------|----------|-----|
| 統合テスト（verify.md） | 外部依存（DB/API/ファイルI/O）、複数コンポーネント結合 | API経由のCRUD操作 |
| ユニットテスト（Auto-Test Targets） | 純粋関数、ビジネスロジック、バリデーション | 入力検証、変換処理 |

**判定フローチャート**:

```
Scenarioを分析
    ↓
外部リソース（DB/API/ファイル）にアクセスする？
    ├─ Yes → 統合テスト（verify.md）
    └─ No
         ↓
    複数コンポーネントを結合する？
    ├─ Yes → 統合テスト（verify.md）
    └─ No → ユニットテスト（Auto-Test Targets）
```

#### Step 3: Auto-Test Targetsセクションへの記載

verify.mdの「Auto-Test Targets」セクションに以下の形式で記載します。

```markdown
## Auto-Test Targets

### Primary Test Cases（主要ケース - Step 2抽出）

| Requirement | Scenario | WHEN/THEN | Priority | Reason |
|-------------|----------|-----------|----------|--------|
| Save Knowledge | 保存成功 | content提供 → 成功レスポンス | P1 | 正常系コアパス |
| Save Knowledge | 空content | content空 → エラー | P2 | バリデーション |
```

**Priority（優先順位）の基準**:

| 優先度 | 種類 | 説明 |
|--------|------|------|
| P1 | 正常系（コアパス） | ビジネスロジックの核となるケース |
| P2 | 致命的境界値 | システム障害につながる可能性のあるケース |
| P3 | ビジネス例外 | 業務上重要だが致命的ではないケース |

## カバレッジチェック（verify.md作成後）

verify.md作成後、spec.mdとのカバレッジをチェックします。

### 実行手順

1. **AIによるカバレッジ分析を実行**
   - spec.mdからRequirements/Scenariosを抽出
   - verify.mdの各テストケースとマッピング
   - coverage.mdを生成

2. **カバレッジ確認**
   - coverage.mdを確認
   - 未カバーの項目がある場合、verify.mdを更新
   - または「Auto-Test Targets」に移動（Step 4で対応）

3. **ブロッキングルール**
   - 「Not Covered」が0であること
   - または「Auto-Test Targets」に明示的に記載されていること

詳細は `.claude/skills/verify-and-coverage/` を参照。

### カバレッジチェックリスト

```
カバレッジ確認:
- [ ] coverage.md生成完了
- [ ] 未カバー項目の対応完了（verify.mdに追加、またはAuto-Test Targetsへ延期を明記）
- [ ] 「Uncovered Items」セクションが空
```

## tasks.md更新

REDステータス確認後、tasks.mdを更新：

```markdown
## 2. 実装フェーズ
- [x] verify.md作成（Runme.dev形式）
- [x] REDステータス確認  ← 完了マーク
- [ ] スケルトン実装
```

## チェックリスト

Step 2完了前に確認：

- [ ] verify.mdにすべてのシナリオを記述済み
- [ ] 各コードブロックに `{"name":"..."}` 属性付与済み
- [ ] `runme list` でコマンド一覧表示確認済み
- [ ] `runme run verify-all` でRED確認済み
- [ ] REDステータスを記録済み
- [ ] **coverage.md生成・確認済み**
- [ ] **未カバー項目の対応完了**
- [ ] tasks.mdを更新済み

## 次のステップ

REDステータス確認後 → **Step 2: Skeleton Green**

verify.mdがパスする最小限の実装（ハードコードやモック可）を行います。

## よくある質問

**Q: Runme.devなしでverify.mdを実行できるか？**

A: できます。verify.mdは通常のShellスクリプトとしても実行可能です。ただし、Runme.devを使用すると名前付き実行、TUI、VS Code統合が利用できます。

**Q: verify.mdとユニットテストの違いは？**

A:
- **verify.md（統合テスト/E2E）**: End-to-Endフロー、外部リソース依存（DB、API、ファイルシステム）、複数コンポーネント結合を確認。実際のcURLやCLIコマンドを実行。
- **ユニットテスト**: ビジネスロジック、純粋関数、バリデーションを確認。外部依存をモック化。高速で大量のテストケースを実行。
- **テストピラミッド**: ユニットテストを大量に、統合テスト（verify.md）を少数に保つことで、高速かつ信頼性の高いテストスイートを構築します。

両方必要ですが、可能な限りユニットテストでカバーし、外部依存や結合コストが高いものだけverify.mdで確認します。

**Q: REDステータスでエラーが出ない場合は？**

A: 既存の実装が部分的に存在する可能性があります。verify.mdの期待値と実際のレスポンスを比較し、差分があればREDと判断します。

**Q: verify-allが長すぎる場合は？**

A: セクションごとに `verify-setup`, `verify-normal-path`, `verify-edge-cases` に分割することを検討します。

## コミット戦略

このステップでのコミットポイント：

**verify.md作成・RED確認後**
```bash
git add openspec/changes/<change-id>/verify.md
git commit -m "test: add integration tests for <feature-name>"
```

詳細は [commit-strategy.md](../references/commit-strategy.md) を参照。
