# Step 5: Archive & Release

## 目的

全テストとverify.mdの最終検証を行い、OpenSpecアーカイブとフィーチャーフラグ有効化を実施して機能をリリースします。

## 最終検証チェックリスト

リリース前に以下を確認します：

```
最終検証:
- [ ] すべてのユニットテストがパス（言語別テストフレームワーク）
- [ ] カバレッジ80%以上（ビジネスロジック・純粋関数を対象）
- [ ] verify.mdがすべてGREEN（runme run verify-all、統合テスト）
- [ ] テストピラミッド確認（ユニット >> 統合）
- [ ] **coverage.md最終確認・100%カバレッジ達成**
- [ ] **spec.md TBDチェック完了（TBD箇所なし）**
- [ ] openspec validate <change-id> --strict がパス
- [ ] フィーチャーフラグ動作確認（ON/OFF両方、フラグ使用時のみ）
- [ ] design.md の Open Questions がすべて解決済み
- [ ] tasks.md のすべてのタスクが完了（`- [x]`）
- [ ] **verify.md / coverage.md正式版昇格準備完了**
- [ ] **マージ後カバレッジ100%確認済み（coverage.md更新済み）**
```

## Step 1: 全テスト検証

### ユニットテスト実行

**言語別テストフレームワーク例**:

```bash
# Python (pytest)
pytest tests/ -v
pytest --cov=lib --cov-report=term-missing  # カバレッジ確認

# Node.js (Jest)
npm test -- --verbose
npm test -- --coverage  # カバレッジ確認

# Go
go test ./... -v
go test -cover ./...  # カバレッジ確認

# Rust
cargo test -- --nocapture
cargo tarpaulin  # カバレッジ確認

# 期待: すべてのテストがパス、カバレッジ80%以上（ビジネスロジック・純粋関数を対象）
```

### verify.md実行（統合テスト）

```bash
cd openspec/changes/<change-id>/

# フィーチャーフラグを有効化
export FEATURE_<NAME>_ENABLED=true

# すべてのテストを実行
runme run verify-all

# 期待: ✅✅✅ All tests GREEN ✅✅✅
```

## 最終カバレッジチェック

アーカイブ前にcoverage.mdを最終確認します。

### 実行手順

1. **coverage.md最終生成**
   - ユニットテストからのカバレッジも反映
   - verify.md + 自動テストで全シナリオがカバーされていることを確認

2. **ブロッキングルール**
   - 「Uncovered Items」セクションが空であること
   - すべてのRequirementが「Covered」
   - 「Auto-Test Targets」に記載された項目は自動テストでカバー済みであること

詳細は `.claude/skills/verify-and-coverage/` を参照。

## Step 1.5: spec.md TBDチェック

### 目的

archive前にspec.mdの未定義箇所（TBD）を検出し、ブロックします。TBDが残っている場合、archiveを実行してはいけません。

### チェック対象

1. **正式版spec.md**: `openspec/specs/*/spec.md`
2. **change内spec.md**: `openspec/changes/<change-id>/specs/*/spec.md`

### チェックコマンド

```bash
# 正式版とchange内のspec.mdをチェック
grep -rn -E "(TBD|tbd|To Be Determined|TODO:|FIXME:)" \
  openspec/specs/*/spec.md \
  openspec/changes/<change-id>/specs/*/spec.md

# 期待: 結果なし（TBD箇所がない）
```

### ブロッキングルール

- TBD箇所が1つでもある場合、archiveを実行しない
- TBD箇所を適切な内容で置換してから再チェック

### TBDが見つかった場合

1. TBD箇所を特定
2. 適切な内容で置換
3. コミット: `git commit -m "docs: resolve TBD in spec.md"`
4. 再チェック

詳細は [tbd-check.md](../references/tbd-check.md) を参照。

## Step 2: OpenSpec検証

### 厳格モードで検証

```bash
# changeの検証
openspec validate <change-id> --strict

# 期待: No errors found
```

### デルタ確認

```bash
# デルタ詳細を確認
openspec show <change-id> --json --deltas-only | jq

# 期待: すべてのrequirementsにscenariosが含まれている
```

## Step 3: フィーチャーフラグ動作確認

**注**: フィーチャーフラグを使用していない場合（完全新規開発等）、このステップはスキップします。

### OFF状態のテスト

```bash
# フィーチャーフラグをOFFに
export FEATURE_<NAME>_ENABLED=false

# APIにアクセス
curl -X POST http://localhost:3000/api/users ...

# 期待: 503 Service Unavailable "Feature not available"
```

### ON状態のテスト

```bash
# フィーチャーフラグをONに
export FEATURE_<NAME>_ENABLED=true

# APIにアクセス
curl -X POST http://localhost:3000/api/users ...

# 期待: 正常なレスポンス（実装された機能が動作）
```

## Step 3.5: verify.md / coverage.md 正式版昇格

### 目的

change内のverify.mdとcoverage.mdを正式版として`specs/<capability>/`に昇格します。

### 昇格対象の確認

```bash
# change内のverify.mdとcoverage.mdを確認
ls openspec/changes/<change-id>/verify.md
ls openspec/changes/<change-id>/coverage.md

# 対象capabilityの確認
ls openspec/changes/<change-id>/specs/

# 期待: verify.mdとcoverage.mdが存在し、対象capabilityが明確
```

### 既存ファイルの確認

```bash
# 正式版verify.md/coverage.mdの存在確認
for cap in $(ls openspec/changes/<change-id>/specs/); do
  echo "=== $cap ==="
  if [ -f "openspec/specs/$cap/verify.md" ]; then
    echo "Existing verify.md found → マージ必要"
  else
    echo "No existing verify.md → 新規昇格"
  fi
  if [ -f "openspec/specs/$cap/coverage.md" ]; then
    echo "Existing coverage.md found → 更新必要"
  else
    echo "No existing coverage.md → 新規昇格"
  fi
done
```

### ケース1: 既存ファイルなし（新規昇格）

```bash
# verify.mdとcoverage.mdを正式版にコピー
cp openspec/changes/<change-id>/verify.md openspec/specs/<capability>/verify.md
cp openspec/changes/<change-id>/coverage.md openspec/specs/<capability>/coverage.md

# コミット
git add openspec/specs/<capability>/verify.md
git add openspec/specs/<capability>/coverage.md
git commit -m "docs: promote verify.md and coverage.md to specs/<capability>"
```

### ケース2: 既存verify.mdあり（マージ必要）

エージェントによるインテリジェントマージを実行:

1. 両方のverify.mdを読み込み
2. マージパターンを判定:
   - **パターン1（新規追加）**: 新しいテストを既存の後に追加
   - **パターン2（微調整）**: 同じシナリオの拡張 → 既存コマンドを更新
   - **パターン3（置換）**: シナリオが根本的に変更 → 既存テストを置換
3. セクション構造を維持してマージ
4. 競合解決・レビュー

詳細は [verify-promotion.md](../references/verify-promotion.md) を参照。

### ケース3: 既存coverage.mdあり（更新）

coverage.mdはverify.mdマージ後に正式版spec.md + 正式版verify.mdから再生成します。既存のcoverage.mdは新しい内容で置き換えられます。

### マージ後カバレッジ確認とcoverage.md更新

マージ後の正式版verify.mdで改めてカバレッジを確認し、coverage.mdを更新:

```bash
# テスト一覧を確認
runme list --filename openspec/specs/<capability>/verify.md

# 全テスト実行
runme run --all --filename openspec/specs/<capability>/verify.md

# 期待: すべてのテストがGREEN
```

**ブロッキングルール**:
- マージ後verify.mdが正式版spec.mdの全Scenarioをカバーしていること
- 「Uncovered Items」が0であること
- カバレッジ不足の場合はテストを追加

詳細は `.claude/skills/verify-and-coverage/` を参照。

### 昇格コミット（マージの場合）

```bash
git add openspec/specs/<capability>/verify.md
git add openspec/specs/<capability>/coverage.md
git commit -m "docs: merge and promote verify.md and coverage.md to specs/<capability>"
```

## Step 4: OpenSpecアーカイブ

**前提条件**: Step 3.5（verify.md / coverage.md正式版昇格）が完了していること

### アーカイブ実行

```bash
# changeをアーカイブ
openspec archive <change-id>

# 対話式プロンプトに従う:
# 1. アーカイブ先ディレクトリ名の確認（YYYY-MM-DD-<change-id>）
# 2. specsの更新確認
# 3. 実行確認（y/n）

# 非対話式（自動化する場合）
openspec archive <change-id> --yes
```

### アーカイブ結果確認

```bash
# アーカイブされたchangeの確認
ls openspec/changes/archive/

# 期待: YYYY-MM-DD-<change-id>/ ディレクトリが作成されている

# specsの更新確認
openspec spec list --long

# 期待: アーカイブしたchangeのrequirementsがspecsに反映されている

# verify.md/coverage.md昇格確認
ls openspec/specs/<capability>/verify.md
ls openspec/specs/<capability>/coverage.md

# 期待: verify.mdとcoverage.mdが正式版として配置されている
```

### アーカイブ後の検証

```bash
# specsの検証
openspec validate --strict

# 期待: No errors found
```

## Step 5: フィーチャーフラグ有効化

**注**: フィーチャーフラグを使用していない場合（完全新規開発等）、このステップはスキップします。

### 方法1: 環境変数削除（推奨）

フィーチャーフラグのデフォルト値を変更し、環境変数を不要にします。

```python
# 例: Python
# Before（開発中）
FEATURE_<NAME>_ENABLED = os.getenv("FEATURE_<NAME>_ENABLED", "false") == "true"

# After（リリース後）
FEATURE_<NAME>_ENABLED = os.getenv("FEATURE_<NAME>_ENABLED", "true") == "true"
#                                                              ^^^^^ デフォルトをtrueに変更
```

```javascript
// 例: Node.js
// Before（開発中）
const FEATURE_ENABLED = process.env.FEATURE_<NAME>_ENABLED === 'true';

// After（リリース後）
const FEATURE_ENABLED = process.env.FEATURE_<NAME>_ENABLED !== 'false';
//                                                             ^^^^^^^ デフォルトをtrueに変更
```

または、フィーチャーフラグコードを完全に削除します：

```python
# 例: Python
# フィーチャーフラグを削除し、常に有効化
@app.post("/api/users", response_model=UserResponse)
def create_user(user: UserCreate):
    # if not FEATURE_<NAME>_ENABLED:  ← 削除
    #     raise HTTPException(...)     ← 削除

    # 機能は常に有効
    db_user = create_user_in_db(...)
    return UserResponse(...)
```

### 方法2: 環境変数設定（段階的リリース）

本番環境の環境変数を設定します。

```bash
# 本番環境の.envファイル（または環境変数設定）
FEATURE_<NAME>_ENABLED=true
```

クラウドプロバイダの環境変数設定例：

```bash
# Heroku
heroku config:set FEATURE_<NAME>_ENABLED=true

# AWS Elastic Beanstalk
eb setenv FEATURE_<NAME>_ENABLED=true

# Google Cloud Run
gcloud run services update <service-name> \
  --update-env-vars FEATURE_<NAME>_ENABLED=true

# Vercel
vercel env add FEATURE_<NAME>_ENABLED production
```

## Step 6: PR #N（リリース）作成

### PR情報

- **ブランチ名**: `release/<change-id>`
- **タイトル**: `[Release] <feature-name>`
- **ラベル**: `release`, `ready-to-deploy`

### PR本文テンプレート

```markdown
## Release: <feature-name>

This PR archives the OpenSpec change and enables the feature in production.

### What's Included

- ✅ OpenSpec archived to `openspec/changes/archive/YYYY-MM-DD-<change-id>/`
- ✅ Specs updated in `openspec/specs/<capability>/`
- ✅ Feature flag enabled (or removed)
- ✅ All tests pass
- ✅ verify.md GREEN

### Verification

**Unit Tests**:
\`\`\`bash
# 例: Python (pytest)
pytest tests/
# PASSED: XX tests, coverage: XX%

# 例: Node.js (Jest)
npm test
# PASS: XX tests, coverage: XX%
\`\`\`

**Integration Tests**:
\`\`\`bash
runme run verify-all
# ✅✅✅ All tests GREEN ✅✅✅
\`\`\`

**OpenSpec Validation**:
\`\`\`bash
openspec validate --strict
# No errors found
\`\`\`

**Test Pyramid Confirmation**:
- ✅ Unit tests: Cover business logic, pure functions, validations
- ✅ Integration tests: Cover End-to-End flows, external dependencies
- ✅ Ratio: Unit tests >> Integration tests

### Feature Flag

**注**: フィーチャーフラグを使用していない場合、このセクションは省略します。

- Before: `FEATURE_<NAME>_ENABLED=false` (default)
- After: `FEATURE_<NAME>_ENABLED=true` (enabled in production)

Or feature flag code removed entirely.

### Related

- PR #2: Skeleton implementation
- PR #3: Logic implementation
- PR #N: Archive and release (this PR)

### Deployment

After merging this PR:
1. Deploy to production
2. Verify feature is available
3. Monitor for issues

### Rollback Plan

If issues occur:
1. Set `FEATURE_<NAME>_ENABLED=false` in production
2. Redeploy

Or revert this PR and redeploy.
```

### PR作成コマンド

```bash
# ブランチ作成
git checkout -b release/<change-id>

# ファイル追加（アーカイブ結果、フィーチャーフラグ変更等）
git add openspec/changes/archive/
git add openspec/specs/
git add lib/  # フィーチャーフラグ変更含む

# コミット
git commit -m "$(cat <<'EOF'
[Release] <feature-name>

Archive OpenSpec change and enable feature in production.
- OpenSpec archived: openspec/changes/archive/YYYY-MM-DD-<change-id>/
- Specs updated: openspec/specs/<capability>/
- Feature flag: enabled (or removed)

All tests pass:
- Unit tests: XX tests, coverage: XX%
- Integration tests: verify.md GREEN
- OpenSpec validation: PASSED

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"

# プッシュ
git push -u origin release/<change-id>

# PR作成
gh pr create --title "[Release] <feature-name>" --body "$(cat PR_BODY.md)"
```

## Step 7: デプロイとモニタリング

### デプロイ

PR #N（リリース）をmainブランチにマージ後、本番環境にデプロイします。

```bash
# mainブランチにマージ済みを確認
git checkout main
git pull origin main

# デプロイ（プロジェクトのデプロイ手順に従う）
# 例: Heroku
git push heroku main

# 例: Vercel
vercel --prod

# 例: Cloud Run
gcloud run deploy <service-name> --source .
```

### 機能確認

```bash
# 本番環境のAPIをテスト
curl -X POST https://production.example.com/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "email": "production-test@example.com",
    "password": "SecurePass123"
  }'

# 期待: 正常なレスポンス
```

### モニタリング

- アプリケーションログを確認
- エラー率を監視
- レスポンスタイムを監視
- ユーザーフィードバックを収集

## tasks.md最終更新

PR #N（リリース）マージ後、tasks.mdを更新：

```markdown
## 3. リリースフェーズ
- [x] 全テスト検証
- [x] openspec validate --strict 実行
- [x] openspec archive <change-id> 実行
- [x] フィーチャーフラグ有効化
- [x] PR #N作成・マージ
- [x] デプロイ完了  ← 完了マーク

✅✅✅ リリース完了 ✅✅✅
```

## 完了チェックリスト

Step 5完了前に確認：

- [ ] すべてのユニットテストがパス（言語別テストフレームワーク）
- [ ] カバレッジ80%以上（ビジネスロジック・純粋関数を対象）
- [ ] verify.mdがすべてGREEN（統合テスト）
- [ ] テストピラミッド確認（ユニット >> 統合）
- [ ] **coverage.md最終確認・100%カバレッジ達成**
- [ ] **spec.md TBDチェック完了（TBD箇所なし）**
- [ ] `openspec validate <change-id> --strict` がパス
- [ ] フィーチャーフラグ動作確認（ON/OFF、フラグ使用時のみ）
- [ ] **verify.md / coverage.md正式版昇格完了**
- [ ] **マージ後カバレッジ100%確認済み（coverage.md更新済み）**
- [ ] `openspec archive <change-id>` 実行済み
- [ ] アーカイブ後の `openspec validate --strict` がパス
- [ ] フィーチャーフラグ有効化（または削除、フラグ使用時のみ）
- [ ] PR #N（リリース）作成・レビュー・マージ済み
- [ ] 本番環境にデプロイ済み
- [ ] 本番環境で機能確認済み
- [ ] tasks.mdを最終更新済み

## ロールバック手順

問題が発生した場合のロールバック手順：

### 方法1: フィーチャーフラグでロールバック（推奨）

```bash
# 本番環境でフィーチャーフラグをOFF
# Heroku
heroku config:set FEATURE_<NAME>_ENABLED=false

# 即座に機能が無効化される（再デプロイ不要）
```

### 方法2: PR #N（リリース）をリバート

```bash
# PR #N（リリース）をリバート
gh pr view <pr-number> --json mergeCommit --jq '.mergeCommit.oid' | \
  xargs git revert

# 再デプロイ
git push origin main
# デプロイ手順に従う
```

## よくある質問

**Q: アーカイブ後にspecsが更新されない場合は？**

A: `openspec archive <change-id> --skip-specs` で実行した可能性があります。手動でspecsを更新するか、アーカイブをやり直します。

**Q: テストピラミッドが崩れている場合（統合テスト >> ユニットテスト）は？**

A: 理想的ではありませんが、リリース前に以下を確認：
- 統合テスト（verify.md）がすべてGREEN
- 外部依存が多い場合、ユニットテストが少なくても許容される場合がある
- 次回の開発でユニットテストを追加し、テストピラミッドを改善

**Q: フィーチャーフラグは必ず削除すべきか？**

A: 削除するかどうかはプロジェクトの方針次第です。以下を考慮：
- 削除するメリット: コードがシンプルになる
- 残すメリット: 緊急時に即座にOFF可能

**Q: フィーチャーフラグを使用していない場合は？**

A: 完全新規開発等でフィーチャーフラグを使用していない場合、Step 3（フィーチャーフラグ動作確認）とStep 5（フィーチャーフラグ有効化）をスキップします。PR #3でもフィーチャーフラグに関する記述を省略します。

**Q: PR #3のマージ後すぐにデプロイすべきか？**

A: プロジェクトのデプロイサイクルに従います。CI/CDが自動デプロイする場合は即座に、手動デプロイの場合は適切なタイミングで実施します。

**Q: アーカイブしたchangeは削除されるのか？**

A: いいえ。`openspec/changes/archive/YYYY-MM-DD-<change-id>/` に移動されるだけで、削除はされません。履歴として残ります。

**Q: 他の言語（Node.js、Go、Rust等）でも同じ方法論を使えるか？**

A: はい。OpenSpecアーカイブ、フィーチャーフラグパターン、テストピラミッドは言語非依存です。各言語のツール（テストフレームワーク、環境変数管理等）で同じパターンを適用できます。

## コミット戦略

このステップでのコミットポイント：

**OpenSpecアーカイブ完了後**
```bash
git add openspec/changes/archive/ openspec/specs/
git commit -m "docs: archive OpenSpec change for <feature-name>"

# verify.md/coverage.md昇格もコミットに含める（まだコミットしていない場合）
git add openspec/specs/<capability>/verify.md
git add openspec/specs/<capability>/coverage.md
```

詳細は [commit-strategy.md](../references/commit-strategy.md) を参照。

## 完了

🎉 機能が本番環境で利用可能になりました！

次の機能開発は再びStep 0（Proposal）から開始します。
