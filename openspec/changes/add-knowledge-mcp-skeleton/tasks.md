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
- [ ] verify.md作成（Runme.dev形式）
- [ ] REDステータス確認
- [ ] GCPプロジェクト基盤整備
  - [ ] Cloud Run サービスアカウント設定
  - [ ] IAMポリシー設定
- [ ] Cloud Run + Buildpacks デプロイ検証（MCPなし最小構成）
  - [ ] uvベースプロジェクト作成（pyproject.toml + uv.lock + Procfile）
  - [ ] 最小限のHTTPサーバー（/health のみ）
  - [ ] `gcloud run deploy --source .` でデプロイ成功確認
- [ ] PR #2a作成・マージ
  - verify.md: test-health GREEN, MCP関連テストは SKIP

### PR #2b: MCPスケルトン
- [ ] MCPサーバー実装
  - [ ] FastMCP プロジェクト構成
  - [ ] HTTP /health エンドポイント（Cloud Run用）
  - [ ] save_knowledge ツール（スタブ）
  - [ ] search_knowledge ツール（スタブ）
- [ ] Cloud Runへ再デプロイ・疎通確認
- [ ] スキップしたMCPテストを有効化（@pytest.mark.skip解除）
- [ ] スケルトン実装完了（全テストGREEN確認）
- [ ] PR #2b作成・マージ

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
