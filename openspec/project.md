# Project Context

## Purpose

開発者が日々のコーディング中に得る断片的なナレッジ（個人ナレッジ）を蓄積し、価値のあるものをAIが自律的に判断してチーム共有ナレッジ（GitHub）へ昇格させるエコシステム。

**GitHub上のMarkdownファイルを唯一の正解（SSoT）とし、Google Cloud上のデータは高速かつ高度な検索を実現するための「レプリカ」として運用する。**

## Tech Stack

### MCP Server (Knowledge Gateway)
- Python 3.11+
- FastAPI（Webフレームワーク）
- FastMCP（MCP Protocol実装）

### Infrastructure
- Google Cloud Run（MCPサーバーホスティング）
- Firestore（ナレッジデータストア - レプリカ）
- Vertex AI Search（高度な検索機能）
- Vertex AI Agent Engine（Remote Knowledge Agent）

### Local Agent
- Claude Code（MCP Client）

### CI/CD & Sync
- GitHub Actions
- Workload Identity Federation

### VCS
- GitHub（SSoT）

## Project Conventions

### Code Style
- Python: ruff（linter & formatter）
- Type hints必須
- docstring: Google style

### Architecture Patterns
- クリーンアーキテクチャの原則に従う
- 依存性注入を活用
- ドメインロジックとインフラストラクチャを分離

### Testing Strategy
- pytest
- 垂直TDDスケルトン戦略を採用
- verify.md（Runme.dev形式）で統合テスト定義

### Git Workflow
- mainブランチへのPR必須
- コミットメッセージ: Conventional Commits
- 小さなコミットを頻繁に

## Domain Context

### ナレッジの種類
- **個人ナレッジ（personal）**: 開発者がローカルで保存するメモ・気づき
- **チームナレッジ（team）**: GitHubに昇格された共有ナレッジ

### ナレッジのステータス
- **draft**: 下書き状態
- **proposed**: 昇格提案中
- **promoted**: GitHubに昇格済み

### 同期方向
- GitHub → Firestore: GitHub Actionsによるプッシュ型同期
- Firestore → GitHub: Remote Agentによる昇格PR作成

## Important Constraints

- GitHubがSSoT（Single Source of Truth）
- Firestoreはあくまでレプリカ
- MCPサーバーは認証付きで公開（将来的にWorkload Identity）
- コスト効率を意識した設計

## External Dependencies

- Google Cloud Platform
  - Cloud Run
  - Firestore
  - Vertex AI Search
  - Vertex AI Agent Engine
- GitHub API
- MCP Protocol
