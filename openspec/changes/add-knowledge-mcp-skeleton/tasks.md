# Tasks: 知識共有MCPサーバーの垂直スケルトン構築

## 1. 提案フェーズ
- [x] proposal.md作成
- [x] spec deltas作成
- [x] PR #1作成・マージ
- [x] 技術検証（FastMCP + Cloud Run構成）→ spike/results.md
- [x] design.md作成
- [x] PR #1b作成・マージ → https://github.com/hyt-sasaki/ai-knowledge-promoter/pull/3

## 2. 実装フェーズ（パターンB: インフラ先行型）

### PR #2a: デプロイ基盤
- [x] verify.md作成（Runme.dev形式）
- [x] REDステータス確認
- [x] GCPプロジェクト基盤整備
  - [x] GCPプロジェクト作成（ai-knowledge-promoter）
  - [x] 課金アカウント紐付け
  - [x] Cloud Run/Cloud Build/Artifact Registry API有効化
- [x] Cloud Run + Buildpacks デプロイ検証（MCPなし最小構成）
  - [x] uvベースプロジェクト作成（pyproject.toml + uv.lock + Procfile）
  - [x] 最小限のHTTPサーバー（/health のみ）
  - [x] `gcloud run deploy --source .` でデプロイ成功確認
- [x] PR #2a作成・マージ → https://github.com/hyt-sasaki/ai-knowledge-promoter/pull/4
  - verify.md: test-health GREEN, MCP関連テストは SKIP

### PR #2b: MCPスケルトン
- [x] MCPサーバー実装
  - [x] FastMCP プロジェクト構成
  - [x] HTTP /health エンドポイント（Cloud Run用）
  - [x] save_knowledge ツール（スタブ）
  - [x] search_knowledge ツール（スタブ）
- [x] Cloud Runへ再デプロイ・疎通確認
- [x] verify.mdのMCPテストを有効化（excludeFromRunAll解除）
- [x] スケルトン実装完了（全テストGREEN確認）
- [x] PR #2b作成・マージ → https://github.com/hyt-sasaki/ai-knowledge-promoter/pull/7

## 3. ロジック実装フェーズ（Phase 2）

### PR #3a: 技術調査（Spike）
- [x] Firestore技術調査
  - [x] google-cloud-firestore 非同期API（AsyncClient）
  - [x] array-contains検索（タグ検索用）
  - [x] タイトル前方一致検索（フルテキスト検索の代替）
  - [x] Cloud Run上でのデフォルト認証
- [x] Cloud Run認証調査（Cloud IAPからCloud Run Invoker権限に変更）
  - [x] Cloud Run Invoker権限設定方法
  - [x] 未認証アクセス無効化手順
  - [x] Claude Codeからの認証トークン送信方法
- [x] OpenSpecドキュメント更新
  - [x] spike/results-phase2.md作成
  - [x] design.md: Phase 2設計判断を追記
  - [x] tasks.md: Phase 2タスクを細分化（本更新）
  - [x] spec.md: Phase 2要件を追記
- [ ] PR #3a作成・マージ

### PR #3b: Cloud Run認証設定
- [ ] Cloud Run Invoker権限設定
- [ ] 未認証アクセス無効化
- [ ] Claude Code MCP設定更新（認証ヘッダー追加）
- [ ] 疎通確認
- [ ] PR #3b作成・マージ

### PR #3c: Firestoreセットアップ
- [ ] Firestoreデータベース作成（Native Mode, asia-northeast1）
- [ ] 依存関係追加（google-cloud-firestore>=2.14.0）
- [ ] Knowledgeモデル作成（models/knowledge.py）
- [ ] KnowledgeRepository作成（repositories/knowledge_repository.py）
- [ ] ユニットテスト（モデル・リポジトリ）
- [ ] PR #3c作成・マージ

### PR #3d: save_knowledge実装
- [ ] ユニットテスト作成（RED）
- [ ] save_knowledge_logic実装（GREEN）
  - [ ] バリデーション（空タイトル・空コンテンツ拒否）
  - [ ] Knowledgeモデル作成
  - [ ] リポジトリ経由でFirestore保存
- [ ] エラーハンドリング
- [ ] verify.md更新（Firestoreテスト追加）
- [ ] PR #3d作成・マージ

### PR #3e: search_knowledge実装
- [ ] ユニットテスト作成（RED）
- [ ] search_knowledge_logic実装（GREEN）
  - [ ] クエリタイプ判定（#始まり→タグ検索、それ以外→タイトル前方一致）
  - [ ] スコア計算（タイトル完全一致=1.0、前方一致=0.9、タグ一致=0.85）
- [ ] verify.md更新（検索テスト追加）
- [ ] PR #3e作成・マージ

## 4. 高度な検索フェーズ（Phase 3）
- [ ] Vertex AI Search統合
- [ ] セマンティック検索実装

## 5. リリースフェーズ
- [ ] verify.md全テストGREEN確認
- [ ] openspec validate --strict 実行
- [ ] openspec archive add-knowledge-mcp-skeleton 実行
- [ ] フィーチャーフラグ有効化
- [ ] PR #N（リリース）作成・マージ
