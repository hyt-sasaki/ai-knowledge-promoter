# ai-knowledge-promoter

AIエージェントを活用し、開発者の断片的な個人ナレッジを収集・蓄積して、チーム共有の資産へと自律的に昇格（Promotion）させるシステムです。FirestoreとVertex AI Searchを基盤に、二層のエージェント構造が実装セッションから「生きた知見」を抽出し、GitHubへのプルリクエスト形式でチーム共有を自動提案します。

## プロジェクト構成

```
ai-knowledge-promoter/
├── mcp-server/          # FastAPI サーバー (main.py, tools/)
│   └── tools/          # Firestore, Vertex AI, GitHub 連携ツール
├── remote-agent/        # Vertex AI エージェントプロンプト
├── infra/              # GCP セットアップスクリプト
├── docs/               # チームナレッジベース
│   └── templates/      # ドキュメントテンプレート (例: knowledge-base-template.md)
├── .github/
│   └── workflows/      # GitHub Actions (例: sync-to-cloud.yml)
├── skills/             # プロンプトテンプレート
└── scripts/            # メンテナンススクリプト
```

## 概要

### 1. `mcp-server/`
FastAPI ベースの MCP サーバー。以下の機能を提供：
- Firestore へのナレッジノート保存
- Vertex AI による AI 処理
- GitHub への PR 作成

### 2. `remote-agent/`
Vertex AI エージェントのプロンプト設定

### 3. `infra/`
GCP リソースのセットアップスクリプト

### 4. `docs/`
チームナレッジベース。`templates/` にはドキュメントテンプレートを配置

### 5. `.github/workflows/`
GitHub Actions 設定。`docs/` の同期などを自動化

### 6. `skills/`
プロンプトテンプレート集

### 7. `scripts/`
メンテナンス・運用スクリプト

## セットアップ

各ディレクトリに実装を追加してください。詳細は各ディレクトリの README を参照してください。

## ライセンス

MIT License
