# Tasks: 知識共有MCPサーバーの垂直スケルトン構築

## 1. 提案フェーズ
- [x] proposal.md作成
- [x] spec deltas作成
- [x] PR #1作成・マージ
- [x] 技術検証（FastMCP + Cloud Run構成）→ spike/results.md
- [x] design.md作成
- [ ] PR #1.5作成・マージ → https://github.com/hyt-sasaki/ai-knowledge-promoter/pull/3

## 2. 実装フェーズ
- [ ] verify.md作成（Runme.dev形式）
- [ ] REDステータス確認
- [ ] GCPプロジェクト基盤整備
  - [ ] Cloud Run サービスアカウント設定
  - [ ] Firestore データベース作成
  - [ ] IAMポリシー設定
- [ ] MCPサーバー実装
  - [ ] FastAPI + FastMCP プロジェクト構成
  - [ ] HTTP /health エンドポイント（Cloud Run用、MCPツールとは別）
  - [ ] save_knowledge ツール（スタブ）
  - [ ] search_knowledge ツール（スタブ）
- [ ] Dockerfile & Cloud Runデプロイ設定
- [ ] スケルトン実装完了（GREEN確認）
- [ ] PR #2作成・マージ

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
- [ ] PR #4作成・マージ
