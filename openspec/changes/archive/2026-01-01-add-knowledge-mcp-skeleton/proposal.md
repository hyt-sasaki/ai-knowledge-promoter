# Change: 知識共有MCPサーバーの垂直スケルトン構築

## Why

開発者が日々のコーディング中に得る断片的なナレッジを蓄積・共有するエコシステムを構築したい。Phase 1として、Local Agent（Claude Code）からCloud Run上のMCPサーバーまで疎通する最小限の垂直スケルトンを構築し、早期にシステム統合を完了させる。

## What Changes

- GCPプロジェクト基盤の整備（Cloud Run、Firestore、IAM設定）
- FastAPI + FastMCPによるMCPサーバーのハローワールド実装
- Local Agent用MCPクライアント設定（Claude Code Skills）
- Cloud Runへのデプロイとエンドツーエンド疎通確認

## Impact

- Affected specs: knowledge-gateway（新規capability）
- Affected code:
  - `src/mcp_server/` - MCPサーバー実装
  - `infrastructure/` - GCPリソース定義
  - `.claude/` - Local Agent設定
