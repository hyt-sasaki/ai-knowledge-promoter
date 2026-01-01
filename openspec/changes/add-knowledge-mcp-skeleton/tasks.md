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
- [ ] PR #2a作成・マージ → https://github.com/hyt-sasaki/ai-knowledge-promoter/pull/4
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
- [ ] PR #2b作成・マージ → https://github.com/hyt-sasaki/ai-knowledge-promoter/pull/7

## 3. ロジック実装フェーズ（Phase 2以降）
- [ ] Firestore連携実装
- [ ] Vertex AI Search統合
- [ ] ユニットテスト実装
- [ ] PR #3作成・マージ

## 4. リリースフェーズ
- [ ] 全テスト検証
- [ ] openspec validate --strict 実行
- [ ] openspec archive add-knowledge-mcp-skeleton 実行
- [ ] フィーチャーフラグ有効化
- [ ] PR #N（リリース）作成・マージ
