# Tasks: 知識共有MCPサーバーの垂直スケルトン構築

## 1. 提案フェーズ
- [x] proposal.md作成
- [x] spec deltas作成
- [ ] 技術検証（FastMCP + Cloud Run構成）
- [ ] design.md作成
- [ ] 提案レビュー・承認

## 2. 実装フェーズ
- [ ] verify.md作成（Runme.dev形式）
- [ ] REDステータス確認
- [ ] GCPプロジェクト基盤整備
  - [ ] Cloud Run サービスアカウント設定
  - [ ] Firestore データベース作成
  - [ ] IAMポリシー設定
- [ ] MCPサーバー実装
  - [ ] FastAPI + FastMCP プロジェクト構成
  - [ ] /healthエンドポイント
  - [ ] save_knowledge ツール（スタブ）
  - [ ] search_knowledge ツール（スタブ）
- [ ] Dockerfile & Cloud Runデプロイ設定
- [ ] スケルトン実装完了（GREEN確認）
- [ ] PR #1作成・マージ

## 3. ロジック実装フェーズ（Phase 2以降）
- [ ] Firestore連携実装
- [ ] Vertex AI Search統合
- [ ] ユニットテスト実装
- [ ] PR #2作成・マージ

## 4. リリースフェーズ
- [ ] 全テスト検証
- [ ] openspec validate --strict 実行
- [ ] openspec archive <change-id> 実行
- [ ] フィーチャーフラグ有効化
- [ ] PR #3作成・マージ
