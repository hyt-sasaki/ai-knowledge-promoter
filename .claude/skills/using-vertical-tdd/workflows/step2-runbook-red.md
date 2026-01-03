# Step 2: Runbook & Red

## 目的

Runme.dev形式でverify.mdを作成し、期待する挙動をcURLやCLIコマンドで記述してRED（失敗）を確認します。

## verify.mdの役割（テストピラミッド）

verify.mdは**統合テスト/E2Eテスト**として機能します。外部依存（DB、API、ファイルI/O）や複数コンポーネントの結合動作を確認します。

ビジネスロジック、純粋関数、バリデーション等は**ユニットテスト**でカバーします（Step 3で実装）。

→ 詳細: [verify-guide.md](../../verify-and-coverage/references/verify-guide.md)

## 配置場所

`openspec/changes/<change-id>/verify.md`

## verify.md作成

**verify-and-coverage Skill** のワークフローに従って作成します。

→ [create-verify.md](../../verify-and-coverage/workflows/create-verify.md)

主な手順:
1. テンプレートをコピー（verify-template.md, README-template.md）
2. 仕様からシナリオを抽出
3. コードブロックに `<prefix>-` 付きの名前を設定（プロジェクト内でユニークにするため）
4. README.mdで一括実行を設定

→ テンプレート: [verify-template.md](../../verify-and-coverage/templates/verify-template.md)
→ テンプレート: [README-template.md](../../verify-and-coverage/templates/README-template.md)

## REDステータス確認

### 実行とRED確認

現在の実装状態（未実装またはスケルトン前）でverify.mdを実行し、失敗を確認します：

```bash
runme run --all --filename verify.md
```

**期待される結果（RED）**:

✅ Setup セクションは成功（データベース接続等）
❌ test-xxx は失敗（404 Not Found または 500 Internal Server Error）
❌ Edge Cases も失敗

**REDの例**:

```
$ runme run <prefix>-test-create-user
curl: (22) The requested URL returned error: 404 Not Found
❌ test-create-user failed
```

### REDステータスの記録

tasks.mdまたはverify.mdのコメントに記録：

```markdown
<!-- RED Status (2025-12-31)
- test-create-user: 404 Not Found ✅ (expected)
- test-get-user: 404 Not Found ✅ (expected)
-->
```

## Auto-Test Targets抽出ガイドライン

verify.md作成時に、spec.mdの各Scenarioをユニットテスト候補として「Auto-Test Targets」セクションに記載します。

### GIVEN/WHEN/THENからの抽出手順

#### Step 1: spec.mdのScenarioをリスト化

spec.mdからGIVEN/WHEN/THEN形式で記述されたScenarioを抽出します。

#### Step 2: 各Scenarioのテストタイプを判定

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

→ 詳細: [check-coverage.md](../../verify-and-coverage/workflows/check-coverage.md)

**ブロッキングルール**:
- 「Not Covered」が0であること
- または「Auto-Test Targets」に明示的に記載されていること

## 中間PRでのテストスキップ戦略

インフラ先行型パターンなど、verify.mdが部分的にREDの状態でPRをマージする場合のテスト管理方法です。

詳細は [pr-splitting-guide.md](../references/pr-splitting-guide.md) を参照してください。

### runme.dev (verify.md) でのスキップ

`excludeFromRunAll` 属性を使用して、一括実行から除外します：

```markdown
```sh {"excludeFromRunAll":"true","name":"<prefix>-test-save-knowledge"}
# 後続PRで実装予定
curl -X POST http://localhost:8080/mcp/tools/save_knowledge ...
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
- [ ] 各コードブロックに `{"name":"<prefix>-..."}` 属性付与済み
- [ ] `runme list --filename verify.md` でコマンド一覧表示確認済み
- [ ] `runme run --all --filename verify.md` でRED確認済み
- [ ] REDステータスを記録済み
- [ ] **coverage.md生成・確認済み**
- [ ] **未カバー項目の対応完了**
- [ ] tasks.mdを更新済み

## 次のステップ

REDステータス確認後 → **Step 3: Skeleton Green**

verify.mdがパスする最小限の実装（ハードコードやモック可）を行います。

## コミット戦略

このステップでのコミットポイント：

**verify.md作成・RED確認後**
```bash
git add openspec/changes/<change-id>/verify.md
git add openspec/changes/<change-id>/README.md
git commit -m "test: add integration tests for <feature-name>"
```

詳細は [commit-strategy.md](../references/commit-strategy.md) を参照。
