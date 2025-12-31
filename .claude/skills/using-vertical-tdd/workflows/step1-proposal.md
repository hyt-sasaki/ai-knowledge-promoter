# Step 1: Proposal（提案作成）

## 目的

OpenSpec提案を作成し、インターフェース（API型、DBスキーマ）とテストシナリオを2人で合意します。

## 実行タイミング

✅ 新機能開発の開始時
✅ 既存機能の大幅な変更時
✅ アーキテクチャ変更時
✅ 破壊的変更（Breaking Changes）の導入時

## 事前準備：コンテキスト確認

```bash
# アクティブな変更を確認
openspec list

# 既存のcapabilityを確認
openspec spec list --long

# 関連するspecの詳細を確認
openspec show <spec-id> --type spec
```

競合する変更がないか、既存のcapabilityを修正すべきか新規作成すべきかを判断します。

## 手順1: 提案作成

```bash
# change-idを決定（kebab-case、verb-led推奨）
# 例: add-user-auth, update-payment-flow, remove-legacy-api

# ディレクトリ構造を手動で作成
mkdir -p openspec/changes/<change-id>/specs/<capability>
```

以下のディレクトリ構造を作成します：

```
openspec/changes/<change-id>/
├── proposal.md
├── tasks.md
└── specs/
    └── <capability>/
        └── spec.md
```

## 手順2: proposal.md記述

`openspec/changes/<change-id>/proposal.md` を以下の構成で記述：

```markdown
# Change: [変更の簡潔な説明]

## Why
[問題と機会を1-2文で説明]

例：
現在、ユーザー認証がパスワードのみで、セキュリティリスクが高い。
二要素認証を導入し、アカウント乗っ取りを防止する。

## What Changes
- [変更内容を箇条書き]
- [破壊的変更には **BREAKING** マークを付ける]

例：
- 二要素認証（TOTP）をログインフローに追加
- ユーザーテーブルに `totp_secret` カラムを追加
- 既存のログインAPIに `/verify-totp` エンドポイントを追加
- **BREAKING**: ログインレスポンスに `requires_totp` フィールドを追加

## Impact
- Affected specs: [影響を受けるcapability一覧]
- Affected code: [主要なファイル・システム]

例：
- Affected specs: auth, user-profile
- Affected code: src/auth/login.py, src/models/user.py, frontend/LoginPage.tsx
```

## 手順3: tasks.md作成

`openspec/changes/<change-id>/tasks.md` を作成し、実装タスクをチェックリスト形式で記述：

```markdown
## 1. 提案フェーズ
- [ ] proposal.md作成
- [ ] spec deltas作成
- [ ] PR #1作成・マージ
- [ ] 技術検証（spike/results.md完成） ← 必要な場合のみ
- [ ] design.md作成 ← 必要な場合のみ
- [ ] PR #1.5作成・マージ ← 技術検証/design.md実施した場合のみ

## 2. 実装フェーズ
- [ ] verify.md作成（Runme.dev形式）
- [ ] REDステータス確認
- [ ] スケルトン実装
- [ ] PR #2作成・マージ
- [ ] ロジック実装
- [ ] ユニットテスト実装
- [ ] PR #3作成・マージ

## 3. リリースフェーズ
- [ ] 全テスト検証
- [ ] openspec validate --strict 実行
- [ ] openspec archive <change-id> 実行
- [ ] フィーチャーフラグ有効化
- [ ] PR #4作成・マージ
```

### 技術検証タスクの判断基準

以下のいずれかに該当する場合、「技術検証」タスクを追加：

✅ 複数のライブラリ・技術選択肢がある
✅ 新しいライブラリの学習コストが高い
✅ パフォーマンス・互換性の懸念がある
✅ 実験的な検証が設計判断に必要

### design.md作成タスクの判断基準

以下のいずれかに該当する場合、「design.md作成」タスクを追加：

✅ クロスカッティング変更（複数サービス/モジュール）
✅ 新しいアーキテクチャパターン導入
✅ 外部依存の追加
✅ データモデルの大幅変更
✅ セキュリティ・パフォーマンス・マイグレーション複雑性

## 手順4: spec deltas作成

`openspec/changes/<change-id>/specs/<capability>/spec.md` を作成：

### ADDED Requirements（新機能）

```markdown
## ADDED Requirements

### Requirement: Two-Factor Authentication
ユーザーはログイン時に二要素認証（TOTP）を使用しなければならない（SHALL）。

#### Scenario: TOTP登録成功
- **WHEN** ユーザーが `/auth/totp/setup` APIを呼び出す
- **THEN** QRコードとシークレットキーが返される
- **AND** ユーザーテーブルに `totp_secret` が保存される

#### Scenario: ログイン時TOTP検証成功
- **WHEN** 有効な認証情報とTOTPコードを `/auth/login` に送信
- **THEN** JWTトークンが返される
- **AND** `requires_totp` フィールドが `false` となる

#### Scenario: TOTP検証失敗
- **WHEN** 無効なTOTPコードを送信
- **THEN** 401エラーが返される
- **AND** エラーメッセージは「Invalid TOTP code」となる
```

### MODIFIED Requirements（既存機能の変更）

**重要**: MODIFIED には既存要件の**完全な内容**をペーストし、変更を反映します。部分的な差分ではなく、全体を記述してください。

```markdown
## MODIFIED Requirements

### Requirement: User Login
ユーザーは有効な認証情報でログインしなければならない（SHALL）。
ログインレスポンスには `requires_totp` フィールドが含まれる（SHALL）。

#### Scenario: ログイン成功（TOTP未設定）
- **WHEN** 有効な認証情報を `/auth/login` に送信
- **AND** ユーザーがTOTPを設定していない
- **THEN** JWTトークンが返される
- **AND** `requires_totp` フィールドが `false` となる

#### Scenario: ログイン成功（TOTP設定済み）
- **WHEN** 有効な認証情報を `/auth/login` に送信
- **AND** ユーザーがTOTPを設定している
- **THEN** `requires_totp` フィールドが `true` となる
- **AND** JWTトークンは返されない
- **AND** `/auth/verify-totp` へのリダイレクトが必要

#### Scenario: ログイン失敗
- **WHEN** 無効な認証情報を送信
- **THEN** 401エラーが返される
```

### REMOVED Requirements（削除）

```markdown
## REMOVED Requirements

### Requirement: Password-Only Authentication
**Reason**: セキュリティ強化のため、パスワードのみの認証を廃止
**Migration**: すべてのユーザーに初回ログイン時にTOTP設定を強制
```

### RENAMED Requirements（名前変更）

```markdown
## RENAMED Requirements

- FROM: `### Requirement: Login`
- TO: `### Requirement: User Authentication`
```

### 重要な注意事項

1. **シナリオは必須**: すべての要件に最低1つの `#### Scenario:` が必要
2. **シナリオ形式**: `#### Scenario: [説明]` の形式を厳守（3つのハッシュやboldは不可）
3. **SHALL/MUST使用**: 規範的要件には SHALL または MUST を使用
4. **完全な記述**: MODIFIED では既存内容を全てコピーし、変更を反映

## 手順5: 検証

```bash
# 厳格モードで検証
openspec validate <change-id> --strict

# デルタの詳細を確認
openspec show <change-id> --json --deltas-only
```

エラーが出た場合は修正し、再度検証します。

### よくあるエラー

**「Change must have at least one delta」**
- `changes/<change-id>/specs/` ディレクトリにspecファイルが存在するか確認
- spec.mdに操作プレフィックス（`## ADDED Requirements` 等）があるか確認

**「Requirement must have at least one scenario」**
- すべての要件に `#### Scenario:` が含まれているか確認
- フォーマットが正確か確認（4つのハッシュ、コロン、スペース、説明）

## 手順6: PR #1作成（Proposal）

提案が完成したらPRを作成してチームレビューを依頼します。

### ブランチ作成

```bash
git checkout -b proposal/<change-id>
```

### コミット

```bash
git add openspec/changes/<change-id>/
git commit -m "docs: add proposal for <feature-name>

- proposal.md: Why/What/Impact を記述
- tasks.md: 実装ステップを定義
- spec deltas: シナリオ付き要件を定義

🤖 Generated with Claude Code"
```

### PR作成

```bash
gh pr create \
  --title "[Proposal] <feature-name>" \
  --body "$(cat <<'EOF'
## 概要
<proposal.mdのWhyセクションを記載>

## スコープ
<tasks.mdの主要タスクを記載>

## レビュー観点
- [ ] Why が明確で説得力がある
- [ ] What Changes が具体的
- [ ] Impact の範囲が適切
- [ ] Spec deltas がシナリオ付きで記述されている
- [ ] tasks.md が実行可能なステップに分割されている
- [ ] openspec validate --strict がパスする

🤖 Generated with Claude Code
EOF
)"
```

### チェックリスト

PR作成前に確認：

- [ ] `openspec validate <change-id> --strict` がパスする
- [ ] proposal.mdのsummaryが明確
- [ ] tasks.mdにステップが記載されている

承認を得てから次のステップに進みます。

## 分岐判定：次のステップ

tasks.mdの内容に応じて次のステップを決定：

### パターン1: 技術検証が必要

```markdown
## 1. 提案フェーズ
- [x] proposal.md作成
- [x] spec deltas作成
- [ ] 技術検証  ← これが未完了
```

→ **Step 1a: Tech Spike** へ進む

### パターン2: design.md作成が必要

```markdown
## 1. 提案フェーズ
- [x] proposal.md作成
- [x] spec deltas作成
- [x] 技術検証（または技術検証タスクなし）
- [ ] design.md作成  ← これが未完了
```

→ **Step 1b: Design** へ進む

### パターン3: すぐ実装開始

```markdown
## 1. 提案フェーズ
- [x] proposal.md作成
- [x] spec deltas作成
- [x] 提案レビュー・承認
（技術検証・design.mdタスクなし）
```

→ **Step 2: Runbook & Red** へ進む

## チェックリスト

提案完成前に確認：

- [ ] `openspec list` でchange-idが表示される
- [ ] `openspec show <change-id>` で提案内容が表示される
- [ ] proposal.mdにWhy/What/Impactが記述されている
- [ ] tasks.mdにチェックリストが記述されている
- [ ] spec deltasにシナリオ付き要件が記述されている
- [ ] `openspec validate <change-id> --strict` がパスする
- [ ] チームでレビュー・承認済み

## コミット戦略

このステップでのコミットポイント：

**OpenSpec検証パス後 → PR #1作成**

詳細は [commit-strategy.md](commit-strategy.md) を参照。

## 参考コマンド

```bash
# 全文検索（既存要件の確認）
rg -n "Requirement:|Scenario:" openspec/specs

# 特定capabilityの詳細確認
openspec show auth --type spec --json

# デルタ詳細のデバッグ
openspec show <change-id> --json | jq '.deltas'
```
