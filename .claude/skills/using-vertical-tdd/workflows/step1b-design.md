# Step 1b: Design（設計文書化）

## 目的

技術検証結果を踏まえ、design.mdで設計判断を文書化します。

## design.md作成基準（OpenSpec準拠）

以下のいずれかに該当する場合、design.mdを作成します：

✅ クロスカッティング変更（複数サービス/モジュールに影響）
✅ 新しいアーキテクチャパターン導入
✅ 外部依存の追加（ライブラリ、API、サービス）
✅ データモデルの大幅変更
✅ セキュリティ・パフォーマンス・マイグレーション複雑性
✅ 技術検証で複数案を比較した結果を反映

### design.md不要な場合

❌ 単一ファイルの変更のみ
❌ 既知のパターンで実装可能
❌ 単純なCRUD操作のみ
❌ 技術スタックが明確で議論不要

## ベストプラクティス調査

design.mdを書く前に、不明確・不確実な箇所について最新のベストプラクティスを調査します。

### 調査が必要な場合

#### Step 1a（技術検証）を実施した場合
- ✅ 技術検証で不明確・不確実性が残った箇所
- ✅ 実装方針は決まったが、細部のパターンが不明な箇所
- ✅ セキュリティ・パフォーマンス・保守性のベストプラクティス確認

#### Step 1aをスキップした場合
- ✅ 技術スタックは明確だが、設計パターンの確認が必要な箇所
- ✅ 既知の技術でも最新のベストプラクティスを確認したい箇所

### 調査手順の優先順位

1. **Context7（最優先）**: 公式ドキュメントの最新情報を調査
2. **Web Search/Web Fetch（補助）**: Context7で情報が不足する場合のみ使用
   - ⚠️ Web検索は情報が古い可能性があるため、Context7で得た公式情報を優先
   - ブログ記事・Qiita・Stack Overflow等は参考程度に

### 追加の技術検証が必要になった場合

ベストプラクティス調査の過程で、以下の状況が発生した場合はStep 1aに戻ることを検討：

- ❗ 新しいアプローチが発見され、比較検証が必要
- ❗ 既存の判断に重大な懸念が浮上
- ❗ 実装方法が複数あり、実験的検証が必要

この場合、tasks.mdを更新し、追加の技術検証を実施します。

## Context7活用パターン

### 1. 設計パターン調査

**例：Next.js App Routerでの状態管理パターン**

```markdown
## Context7調査手順

1. **ライブラリIDを解決**
   - libraryName: "Next.js"
   - query: "App Routerでの状態管理パターンとベストプラクティス"
   - 結果: `/vercel/next.js`

2. **公式推奨パターン調査**
   - libraryId: `/vercel/next.js`
   - query: "state management patterns app router best practices"
   - 結果メモ:
     - Server ComponentsではURL state推奨（searchParams）
     - Client ComponentsではReact Context推奨
     - グローバル状態はZustandやJotaiを検討
     - Reduxは避ける（App Routerと相性悪い）

3. **調査結果をdesign.mdに反映**
   - Decisionsセクションに「URL state + React Context」を採用理由として記載
   - Alternatives consideredに「Redux（非推奨）」を記載
```

### 2. セキュリティベストプラクティス調査

**例：FastAPI認証フロー**

```markdown
## Context7調査手順

1. **FastAPI公式ドキュメント調査**
   - libraryId: `/tiangolo/fastapi`
   - query: "authentication security best practices JWT OAuth2"
   - 結果メモ:
     - JWTトークンは短命（15分）推奨
     - Refresh tokenでアクセストークン更新
     - HTTPS必須
     - セキュリティヘッダー設定（CORS, CSP等）

2. **OWASPガイドライン調査**
   - libraryId: `/OWASP/CheatSheetSeries`（存在する場合）
   - query: "JWT authentication best practices"
   - 結果メモ:
     - JWTシークレットは環境変数で管理
     - アルゴリズムはHS256またはRS256
     - `none`アルゴリズムを拒否

3. **調査結果をdesign.mdに反映**
   - Decisionsセクションに「JWT 15分有効期限 + Refresh token」を記載
   - Risks / Trade-offsセクションに「トークン漏洩リスク → HTTPS必須」を記載
```

### 3. パフォーマンス最適化パターン調査

**例：React Server Componentsでのデータフェッチ最適化**

```markdown
## Context7調査手順

1. **Next.js最適化パターン調査**
   - libraryId: `/vercel/next.js`
   - query: "data fetching performance optimization server components"
   - 結果メモ:
     - fetch()は自動デデュープ
     - Parallel data fetching推奨（Promise.all）
     - Streaming SSRでTTFB改善
     - Suspenseで段階的レンダリング

2. **調査結果をdesign.mdに反映**
   - Architectureセクションに「Parallel data fetching + Streaming SSR」を記載
   - Decisionsセクションに「Suspenseで段階的レンダリング」を採用理由として記載
```

## design.md構成（OpenSpec推奨）

`openspec/changes/<change-id>/design.md` を以下の構成で作成：

### 最小構成テンプレート

```markdown
## Context
[背景、制約、ステークホルダー]

spike/results.mdの検証結果を踏まえ、〜を設計します。
Context7で調査した最新ベストプラクティスを適用します。

## Goals / Non-Goals
- Goals: [...]
- Non-Goals: [...]

## Decisions
- Decision: [何を決定したか]
- Rationale: [なぜその判断をしたか（spike/results.md、Context7調査結果を引用）]
- Alternatives considered: [検討した他の選択肢と却下理由]

## Architecture
[Context7で調査した最新パターンを適用]

## Risks / Trade-offs
- [Risk] → Mitigation

## Migration Plan
[段階的な移行手順、ロールバック方法]

## Open Questions
[未解決の疑問点]
```

### 記述例：FastAPI認証機能のdesign.md

```markdown
## Context

ユーザー認証機能を追加します。
spike/results.mdの検証により、FastAPI-Usersを採用することを決定しました。
Context7でFastAPIとOWASPのセキュリティベストプラクティスを調査し、設計に反映します。

## Goals / Non-Goals

### Goals
- JWT認証の実装
- 短命トークン（15分）+ Refresh token
- OWASP推奨のセキュリティ設定

### Non-Goals
- OAuth2外部プロバイダ統合（将来的に検討）
- 多要素認証（別のchangeで実装）

## Decisions

### Decision 1: FastAPI-Usersを採用

**Rationale**:
- spike/results.mdの検証により、セットアップ時間が3倍速く、学習コストが低い
- パフォーマンス差は5ms（許容範囲内）
- 当面の要件（基本的なユーザー認証）には十分

**Alternatives considered**:
- Authlib: 柔軟性は高いが、学習コストが高く、セットアップ時間が90分（FastAPI-Usersは30分）
- 自前実装: セキュリティリスクが高く、車輪の再発明

### Decision 2: JWT 15分有効期限 + Refresh token

**Rationale**:
- Context7でFastAPI公式ドキュメント（`/tiangolo/fastapi`）を調査
- OWASP推奨に従い、短命トークンでセキュリティリスクを最小化
- Refresh tokenでユーザー体験を損なわない

**Alternatives considered**:
- 長命トークン（24時間）: トークン漏洩時のリスクが高い
- トークンなし（セッションのみ）: SPA/モバイルアプリとの互換性が低い

### Decision 3: セキュリティヘッダー設定

**Rationale**:
- Context7でOWASP CheatSheet調査
- CORS, CSP, HSTS, X-Content-Type-Optionsを設定
- FastAPI標準ミドルウェアで実装可能

## Architecture

### 認証フロー

\`\`\`
1. ユーザー登録
   POST /auth/register
   → ユーザーテーブルに挿入
   → パスワードはbcryptでハッシュ化

2. ログイン
   POST /auth/login
   → 認証情報検証
   → JWTアクセストークン（15分）+ Refresh token（7日）発行

3. トークン更新
   POST /auth/refresh
   → Refresh token検証
   → 新しいアクセストークン発行

4. 保護されたエンドポイント
   GET /api/protected
   Authorization: Bearer <access_token>
   → JWTデコード・検証
   → ユーザー情報取得
\`\`\`

### データモデル

\`\`\`python
class User(Base):
    __tablename__ = "users"
    id = Column(UUID, primary_key=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
\`\`\`

### セキュリティ設定（Context7調査結果を反映）

- **HTTPS必須**: 本番環境ではHTTPS強制
- **CORS設定**: 許可するオリジンを明示的に列挙
- **CSP**: `Content-Security-Policy: default-src 'self'`
- **JWT署名**: HS256アルゴリズム、シークレットは環境変数

## Risks / Trade-offs

### Risk 1: トークン漏洩
**Mitigation**:
- HTTPS必須（HTTP接続を拒否）
- 短命トークン（15分）でリスク最小化
- Refresh tokenはHTTPOnly cookie（XSS対策）

### Risk 2: パスワード総当たり攻撃
**Mitigation**:
- レート制限（FastAPI-Limiter使用）
- 5回失敗でアカウント一時ロック

### Trade-off: Refresh token管理の複雑さ
- 短命トークンのため、Refresh tokenロジックが必要
- 実装コスト増加（約2-3時間）
- ただし、セキュリティ向上のため許容

## Migration Plan

### フェーズ1: スケルトン実装
- ユーザーテーブル作成
- FastAPI-Usersセットアップ
- `/auth/register`, `/auth/login`エンドポイント（ハードコードレスポンス可）

### フェーズ2: ロジック実装
- パスワードハッシュ化
- JWT発行・検証ロジック
- Refresh tokenロジック

### フェーズ3: セキュリティ強化
- HTTPS強制
- セキュリティヘッダー設定
- レート制限実装

### ロールバック方法
- フィーチャーフラグ `FEATURE_AUTH_ENABLED=false` で無効化
- データベースマイグレーションはロールバックスクリプト用意

## Open Questions

- [ ] Refresh tokenの保存先（DB vs Redis）
- [ ] パスワードリセット機能は同じchangeに含めるか、別changeにするか
- [ ] メール検証は初期実装に含めるか
```

## tasks.md更新

design.md完成後、tasks.mdを更新します：

```markdown
## 1. 提案フェーズ
- [x] proposal.md作成
- [x] spec deltas作成
- [x] 技術検証（spike/results.md完成）
- [x] design.md作成  ← 完了マーク
- [ ] 提案レビュー・承認
```

## チェックリスト

design.md完成前に確認：

- [ ] Contextセクションでspike/results.mdを参照
- [ ] Context7で調査したベストプラクティスを反映
- [ ] Decisionsセクションで各判断の理由を明記
- [ ] Alternatives consideredで却下した選択肢を説明
- [ ] Architectureセクションで具体的なパターンを図示
- [ ] Risks / Trade-offsでリスクと緩和策を列挙
- [ ] Migration Planで段階的な移行手順を記載
- [ ] Open Questionsで未解決事項を明記
- [ ] tasks.mdを更新済み

## PR #1b作成（任意）

Designを実施した場合、別ブランチでPRを作成してチームレビューを依頼します。

**注**: Tech Spikeのみの場合は PR #1a として別途作成することも可能です。

### ブランチ作成

```bash
git checkout main
git checkout -b design/<change-id>
```

### コミット

```bash
git add openspec/changes/<change-id>/spike/
git add openspec/changes/<change-id>/design.md
git commit -m "docs: add tech spike and design for <feature-name>

- spike/results.md: 技術検証結果を記録
- design.md: 設計判断を文書化

🤖 Generated with Claude Code"
```

### PR作成

```bash
gh pr create \
  --title "[Design] <feature-name>" \
  --body "$(cat <<'EOF'
## 技術検証結果
<spike/results.mdの概要>

## 設計判断
<design.mdの主要決定事項>

## レビュー観点
- [ ] 技術選定は妥当か
- [ ] 設計判断の根拠は明確か
- [ ] Open Questionsは解決されているか

🤖 Generated with Claude Code
EOF
)"
```

### PR #1bをスキップする場合

以下の場合はPR #1bを作成せず、Step 2（Runbook & Red）に進みます：

- 技術選定が不要（既存パターンの踏襲）
- 設計が自明（シンプルな機能追加）
- チームで事前合意済み

## 次のステップ

design.md承認後 → **Step 2: Runbook & Red**

design.mdの設計に基づき、verify.mdで期待する挙動を記述します。

## よくある質問

**Q: spike/results.mdとdesign.mdの違いは？**

A: spike/results.mdは「実験結果」、design.mdは「最終設計判断」です。spike/results.mdの推奨アプローチをdesign.mdで採用し、詳細化します。

**Q: Context7で情報が見つからない場合は？**

A: 公式ドキュメント、GitHub、技術ブログを直接参照し、その旨をdesign.mdに記載します。

**Q: design.mdはどこまで詳細に書くべきか？**

A: 実装者が迷わない程度。コード例は最小限で、主に「なぜ」その判断をしたかを記述します。

**Q: Open Questionsが多い場合はどうするか？**

A: 2-3個までなら許容。それ以上ある場合は、追加の技術検証（Step 1aに戻る）または質問を解決してから進めます。

## コミット戦略

このステップでのコミットポイント：

**design.md完成後 → PR #1b作成（任意）**

詳細は [commit-strategy.md](../references/commit-strategy.md) を参照。
