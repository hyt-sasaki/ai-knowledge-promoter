# 知識共有MCPサーバー：プロジェクトロードマップ

## 1. システム設計 (Design)

### 1.1 システム概要

開発者が日々のコーディング中に得る断片的なナレッジ（個人ナレッジ）を蓄積し、価値のあるものをAIが自律的に判断してチーム共有ナレッジ（GitHub）へ昇格させるエコシステム。
**GitHub上のMarkdownファイルを唯一の正解（SSoT）とし、Google Cloud上のデータは高速かつ高度な検索を実現するための「レプリカ」として運用する。**

### 1.2 アーキテクチャ構成

#### 各コンポーネントの役割

* **MCP Server (Knowledge Gateway)**:
  * すべてのナレッジ操作のゲートウェイ。Cloud Run 上でホスティングされる。
  * **Webhook Endpoint**: GitHub Actions からの同期リクエスト（HTTP POST）を受け付け、Markdown をパースして Vector Search 2.0 へ書き込む機能を備える。

* **Local Coding Agent (Claude Code)**:
  * MCP 経由でナレッジの保存・検索を行う。

* **Remote Knowledge Agent (Vertex AI Agent Engine)**:
  * 昇格判定を行い、MCP 経由で GitHub に PR を作成する。

* **GitHub (SSoT)**:
  * ナレッジの正本。マージをトリガーに GitHub Actions を起動する。

### 1.3 データ同期戦略 (Synchronization)

GitHub Actions を利用した、GitHub → Vector Search 2.0 へのプッシュ型同期を採用する。

1. **Trigger**: `main` ブランチの特定のディレクトリ（例: `docs/*.md`）に変更がマージされる。
2. **GitHub Actions**:
   * 変更されたファイルの内容を取得。
   * MCP サーバーの同期用エンドポイント（例: `POST /sync`）に対してデータを送信。
3. **MCP Server**:
   * 受信した内容を Vector Search 2.0 の `status: promoted`, `source: team` として保存・更新する。

### 1.4 データモデル (Vector Search 2.0 Collection)

Vector Search 2.0 Collection で以下の構造を維持する。Auto-Embeddingsにより、ベクトルは自動生成される。

| フィールド名 | 型 | 説明 |
| ----- | ----- | ----- |
| `id` | string | ドキュメントID |
| `title` | string | ナレッジのタイトル |
| `content` | string | ナレッジの本文 |
| `tags` | array | タグのリスト |
| `user_id` | string | `system:github` または開発者の識別子 |
| `source` | string | `personal` / `team` |
| `status` | string | `draft` / `proposed` / `promoted` |
| `path` | string | GitHub上のファイルパス (同期時のキー) |
| `created_at` | string | 作成日時（ISO 8601） |
| `updated_at` | string | 最終更新日時（ISO 8601） |

#### ベクトルスキーマ

```python
{
    "content_embedding": {
        "dense_vector": {
            "dimensions": 768,
            "vertex_embedding_config": {
                "model_id": "gemini-embedding-001",
                "text_template": "{title} {content}",
                "task_type": "RETRIEVAL_DOCUMENT",
            },
        },
    },
}
```

## 2. 開発ロードマップ (Roadmap & Tasks)

### Phase 1: 垂直スケルトンの構築 (Local to Agent)

- [ ] **1.1 GCP プロジェクト基盤の整備**
- [ ] **1.2 MCP サーバーのハローワールド** (FastAPI等のWebフレームワークを内包)
- [ ] **1.3 AIエージェントとの結合テスト**

### Phase 2: 個人ナレッジの永続化と検索

- [ ] **2.1 Vector Search 2.0 データモデリングと実装**
  - [ ] Collection作成（Auto-Embeddings設定含む）
  - [ ] Cloud Run Invoker認証の有効化
  - [ ] Repositoryパターンによるインフラ層の抽象化
- [ ] **2.2 セマンティック検索の実装**
  - [ ] save_knowledgeツールでVector Search 2.0に永続化
  - [ ] search_knowledgeツールでセマンティック検索
- [ ] **[垂直統合Check 1]** 保存したメモがセマンティック検索結果として返ってくるか確認

**Phase 2での制限事項（後続Phaseで対応）:**
- `user_id`: 固定値 "anonymous" を使用（Phase 3で実ユーザーID対応）

### Phase 3: Remote Agent による知的自動化

- [ ] **3.1 Remote Knowledge Agent の構築 (Agent Engine)**
- [ ] **3.2 高度なナレッジ操作ツールの追加**
- [ ] **[垂直統合Check 2]** AIが自発的にPR作成を提案してくるか確認

### Phase 4: チーム共有と同期メカニズムの完遂

- [ ] **4.1 GitHub 連携の実装 (in MCP Server)**
- [ ] **4.2 同期用エンドポイントの実装 (POST /sync)**
- [ ] **4.3 GitHub Actions Workflow の作成**
- [ ] **4.4 エンドツーエンド・シナリオテスト**

### Optional: 開発体験向上

- [ ] **O.1 Local Agent 用 Skills の整備**
  - Claude Code用のカスタムスキル（ナレッジ保存・検索のショートカット等）

## 3. 技術スタック (MVP)

* **Local Agent**: Claude Code
* **Knowledge Gateway**: MCP Server (Python / FastAPI + FastMCP)
* **Remote Agent**: Vertex AI Agent Engine
* **CI/CD & Sync**: GitHub Actions + Workload Identity Federation
* **Infrastructure**: Cloud Run, Vertex AI Vector Search 2.0
* **VCS**: GitHub (SSoT)
