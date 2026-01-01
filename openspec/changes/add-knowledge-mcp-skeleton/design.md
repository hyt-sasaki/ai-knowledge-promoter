# Design: 知識共有MCPサーバーの垂直スケルトン構築

## Context

開発者が日々のコーディング中に得る断片的なナレッジを蓄積・共有するエコシステムを構築するため、Phase 1として垂直スケルトンを構築します。

spike/results.mdの技術検証により、FastMCP + Cloud Run構成が技術的に妥当であることを確認しました。本ドキュメントでは、その検証結果を踏まえた設計判断を文書化します。

### 制約

- GCPをインフラ基盤として使用
- Claude Code（MCP Client）からアクセス可能であること
- Phase 1はスタブ実装（Firestore連携はPhase 2以降）

## Goals / Non-Goals

### Goals

- Cloud RunでFastMCPサーバーをホスティング
- `save_knowledge`、`search_knowledge`ツールのスタブ実装
- ヘルスチェックエンドポイント（`/health`）の提供
- Claude CodeからMCPツールを呼び出せる状態

### Non-Goals

- Firestore連携（Phase 2）
- Vertex AI Search統合（Phase 2）
- Cloud IAP設定（Phase 1では開発用途のため、認証なしで進める）

## Decisions

### Decision 1: FastMCP 2.0を採用（MCP公式SDKではなく）

**Rationale**:

spike/results.mdの検証により、MCP公式Python SDK（`mcp`）とFastMCP 2.0（`fastmcp`）を比較検討した結果、FastMCP 2.0を採用する。

1. **基本APIは同一**: インポートパス以外は公式SDKと同じデコレータベースのAPI
2. **将来の移行不要**: Phase 2以降で認証やComposition機能が必要になっても移行作業なし
3. **追加機能は使わなければ影響しない**: エンタープライズ認証等は明示的に有効化しない限り無効
4. **活発なメンテナンス**: 本番向けドキュメントが充実

**注意事項**:
- `fastmcp<3`でバージョンをピン留め（3.0で破壊的変更予定）
- Phase 2以降でCloud IAPを導入予定のため、FastMCP 2.0のエンタープライズ認証機能は不使用

**Alternatives considered**:

| 選択肢 | 評価 | 却下理由 |
|--------|------|----------|
| MCP公式SDK (`mcp`) | △ | 基本機能のみ。将来FastMCP 2.0の機能が必要になった場合、移行作業が発生 |
| FastAPI MCP | × | FastAPIエンドポイントをMCPとして公開する用途向け。MCPファースト設計には不向き |
| 自前MCP実装 | × | プロトコル実装コストが高く、車輪の再発明 |

### Decision 2: Cloud Run + HTTPトランスポート + ステートレスモード

**Rationale**:
- FastMCPのHTTPトランスポート（Streamable HTTP）がCloud Runと相性が良い
- `stateless_http=True`で水平スケーリング対応（セッションアフィニティ不要）
- サーバーレスでコスト効率が良い（使用時のみ課金）
- GCPの他サービス（Firestore、Vertex AI）との統合が容易
- `@mcp.custom_route`でヘルスチェックエンドポイント、Webhookエンドポイントを追加可能

**トランスポート選択**:

| トランスポート | 採用 | 理由 |
|---------------|------|------|
| HTTP（Streamable） | ✅ | 双方向ストリーミング、複数クライアント対応、ステートレスモード |
| STDIO | ❌ | ローカルCLI向け、Webサービス不適 |
| SSE | ❌ | レガシー、HTTPに置き換え |

**Phase 4対応**:
- `@mcp.custom_route("/sync", methods=["POST"])`でGitHub Actions同期用Webhookを追加可能
- ロードマップ（`docs/roadmap.md`）の「Webhook Endpoint」要件に対応

**Alternatives considered**:
- Cloud Functions: WebSocket/長時間接続に制限があり、MCPプロトコルに不向き
- GKE: 今回の規模ではオーバーエンジニアリング
- Compute Engine: サーバーレスのメリットが得られない

### Decision 3: uv + Google Cloud Buildpacksによるデプロイ

**Rationale**:
- uvは高速なPythonパッケージマネージャー（Rust製）
- `pyproject.toml` + `uv.lock`で依存関係を管理（`requirements.txt`は不使用）
- **Google Cloud BuildpacksがuvをGA（一般提供）でサポート**
- Dockerfileなしでソースからデプロイ可能

**プロジェクト構成**:
- `pyproject.toml`: プロジェクトメタデータと依存関係定義
- `uv.lock`: 依存関係のロックファイル（再現性保証）
- 開発用依存関係は`[dependency-groups].dev`に分離
- **Dockerfile不要**: Buildpacksが`pyproject.toml` + `uv.lock`を自動検出

**Buildpacksのuv検出条件**:
- `uv.lock` + `pyproject.toml`が存在 → 自動的にuvを使用
- Python 3.13以降: pyproject.toml対応がGA
- Python 3.12以前: Preview（`GOOGLE_PYTHON_PACKAGE_MANAGER=uv`で明示指定可能）

**デプロイコマンド**:
```bash
gcloud run deploy SERVICE --source .
```

**Alternatives considered**:
- pip + requirements.txt: 従来のパターンだが、ロックファイル管理が煩雑
- Poetry: 機能は豊富だが、uvより低速。Buildpacks対応あり
- Dockerfile手動管理: カスタマイズ可能だが、メンテナンスコスト増

### Decision 4: スタブ実装でスケルトン構築

**Rationale**:
- 垂直TDD戦略に基づき、まずUI（Claude Code）からDB（将来のFirestore）までの疎通を優先
- ビジネスロジックはPhase 2以降で実装
- 早期にシステム統合を完了させ、リスクを低減

## Architecture

### システム構成図

```
┌─────────────────┐      HTTPS      ┌─────────────────┐
│  Claude Code    │ ◄──────────────► │   Cloud Run     │
│  (MCP Client)   │   MCP over HTTP  │   (FastMCP)     │
│                 │                  │                 │
│  .claude/       │                  │  /health (GET)  │
│  mcp_servers.json                  │  /mcp (MCP)     │
└─────────────────┘                  └────────┬────────┘
                                              │
                                              │ Phase 2
                                              ▼
                                     ┌─────────────────┐
                                     │   Firestore     │
                                     │   (将来)        │
                                     └─────────────────┘
```

### ディレクトリ構成

```
src/mcp_server/
├── __init__.py
├── main.py              # FastMCPサーバーエントリポイント
└── tools/
    ├── __init__.py
    ├── save_knowledge.py    # save_knowledgeツール
    └── search_knowledge.py  # search_knowledgeツール

pyproject.toml           # プロジェクトメタデータ・依存関係
uv.lock                  # 依存関係ロックファイル（自動生成）
Procfile                 # Buildpacks用エントリポイント定義

infrastructure/
└── terraform/           # Terraform設定（将来）
    └── main.tf
```

**注**: Dockerfileは不要。Google Cloud Buildpacksが`pyproject.toml` + `uv.lock`を自動検出してビルド。

### pyproject.toml

```toml
[project]
name = "knowledge-mcp-server"
version = "0.1.0"
description = "Knowledge sharing MCP server for Claude Code"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "fastmcp<3",
    "starlette",
]

[dependency-groups]
dev = [
    "pytest",
    "pytest-asyncio",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

### Procfile

Buildpacksはエントリポイントを`Procfile`で指定：

```
web: python -m mcp_server.main
```

**注**: Cloud Runは`PORT`環境変数を自動設定。アプリケーション側で`PORT`を読み取ってリッスン。

### サーバー初期化

```python
from fastmcp import FastMCP

# ステートレスモードでCloud Run最適化
mcp = FastMCP("KnowledgeGateway", stateless_http=True)
```

### MCPツール定義

#### save_knowledge

```python
import uuid

@mcp.tool
def save_knowledge(
    title: str,
    content: str,
    tags: list[str] = []
) -> dict:
    """
    ナレッジを保存する。

    Args:
        title: ナレッジのタイトル
        content: ナレッジの本文
        tags: タグのリスト（オプション）

    Returns:
        保存結果（id, title, status）
    """
    # Phase 1: スタブ実装
    return {
        "status": "saved",
        "id": "stub-id-" + str(uuid.uuid4())[:8],
        "title": title
    }
```

#### search_knowledge

```python
@mcp.tool
def search_knowledge(
    query: str,
    limit: int = 10
) -> list[dict]:
    """
    ナレッジを検索する。

    Args:
        query: 検索クエリ
        limit: 取得件数の上限（デフォルト10）

    Returns:
        検索結果のリスト（id, title, score）
    """
    # Phase 1: スタブ実装
    return [
        {"id": "stub-1", "title": f"Sample: {query}", "score": 0.95},
        {"id": "stub-2", "title": "Related Knowledge", "score": 0.85}
    ]
```

### ヘルスチェック

Cloud Runのヘルスチェック用にHTTPエンドポイントを提供：

```python
@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> PlainTextResponse:
    return PlainTextResponse("OK")
```

### 環境変数

| 変数名 | 説明 | デフォルト値 |
|--------|------|-------------|
| `PORT` | サーバーポート | 8080 |
| `FEATURE_KNOWLEDGE_MCP_ENABLED` | フィーチャーフラグ | false |

## Risks / Trade-offs

### Risk 1: MCPプロトコルのHTTPマッピング

**Risk**: FastMCPのHTTPトランスポート実装が十分に成熟していない可能性

**Mitigation**:
- spike/results.mdで基本動作を確認済み
- FastMCPは活発に開発されており、GitHubスターも多い
- 問題発生時はissueで報告、workaround実装

### Risk 2: Cloud Runのコールドスタート

**Risk**: コールドスタート時にレスポンスが遅延する可能性

**Mitigation**:
- Phase 1では許容（開発用途）
- 必要に応じてmin-instances=1を設定
- 本番運用時はCloud Run常時稼働オプションを検討

### Trade-off: スタブ実装の技術的負債

- Phase 1ではスタブ実装のため、Phase 2で実装差し替えが必要
- ただし、インターフェース（ツール定義）は維持するため、クライアント側の変更は不要
- 垂直TDDの原則に従い、早期統合のメリットが上回る

## Migration Plan

### Phase 1: スケルトン実装（今回）

1. GCPプロジェクト基盤整備
   - Cloud Runサービスアカウント設定
   - IAMポリシー設定
2. MCPサーバースケルトン実装
   - FastMCP + ヘルスチェック
   - `save_knowledge`、`search_knowledge`スタブ
3. Cloud Runデプロイ
4. Claude Code MCP設定
5. エンドツーエンド疎通確認

### Phase 2: ロジック実装 + 認証基盤（将来）

1. **Cloud IAP設定（認証基盤）** ← 実データを扱う前に必須
   - Cloud Run サービスへのIAP有効化
   - 許可ユーザー/グループのホワイトリスト設定（IAM `roles/iap.httpsResourceAccessor`）
   - Claude Code MCP設定にIAP認証ヘッダー追加
2. Firestoreデータベース作成
3. `save_knowledge`のFirestore連携
4. `search_knowledge`の基本検索実装

**Cloud IAP設定の理由**:
- Phase 2から実データ（ナレッジ）を永続化するため、認証なしでは情報漏洩リスク
- ホワイトリスト方式で許可されたユーザーのみアクセス可能
- Cloud Runに直接IAP設定可能（ロードバランサー不要）

### Phase 3: 高度な検索（将来）

1. Vertex AI Search統合
2. セマンティック検索実装

### ロールバック方法

- フィーチャーフラグ `FEATURE_KNOWLEDGE_MCP_ENABLED=false` で無効化
- Cloud Runサービスを削除またはトラフィック0%に設定

## Open Questions

- [x] FastMCP + Cloud Run構成は技術的に妥当か → spike/results.mdで確認済み
- [x] 認証方式 → Cloud IAP（ロードバランサー不要でCloud Runに直接設定可能）
- [x] マルチテナント対応の必要性 → 不要
- [x] MCP公式SDK vs FastMCP 2.0 → FastMCP 2.0を採用（将来の移行不要、基本APIは同一）

---

## Phase 2 設計判断

spike/results-phase2.mdの技術検証により、Phase 2の設計判断を追記する。

### Decision 5: Cloud Run Invoker権限を採用（Cloud IAPではなく）

**Rationale**:

spike/results-phase2.mdの検証により、Cloud IAPとCloud Run Invoker権限を比較検討した結果、Phase 2ではCloud Run Invoker権限を採用する。

1. **シンプルさ**: Cloud Run Invoker権限は追加のコンポーネント不要
2. **組織制約なし**: Cloud IAPは組織内プロジェクト必須だが、Invoker権限は制約なし
3. **十分なセキュリティ**: `--no-allow-unauthenticated`で未認証アクセスを無効化
4. **将来の移行性**: 必要に応じてCloud IAPへの移行も容易

**設定手順**:
```bash
# 未認証アクセスを無効化
gcloud run services update knowledge-mcp-server \
  --region asia-northeast1 \
  --no-allow-unauthenticated

# ユーザーにInvoker権限を付与
gcloud run services add-iam-policy-binding knowledge-mcp-server \
  --region asia-northeast1 \
  --member="user:your-email@example.com" \
  --role="roles/run.invoker"
```

**Claude Codeからの認証**:
```bash
# IDトークンを取得してMCPサーバーに接続
claude mcp add --transport http knowledge-gateway \
  https://knowledge-mcp-server-xxxxx.run.app/mcp \
  --header "Authorization: Bearer $(gcloud auth print-identity-token)"
```

**Alternatives considered**:

| 選択肢 | 評価 | 却下理由 |
|--------|------|----------|
| Cloud IAP | △ | 組織内プロジェクト必須、ベータ版、セットアップが複雑 |
| 認証なし | × | 実データを扱うため、セキュリティリスクが高い |

### Decision 6: Firestore非同期API（AsyncClient）を採用

**Rationale**:
- FastMCPのツールは非同期関数として定義可能
- `AsyncClient`を使用することでI/Oブロッキングを回避
- Cloud Run上では Application Default Credentials で自動認証

**コード例**:
```python
from google.cloud import firestore

# Cloud Run上では認証情報の明示的な設定は不要
db = firestore.AsyncClient()

async def save_to_firestore(data: dict) -> str:
    doc_ref = db.collection('knowledge').document()
    await doc_ref.set(data)
    return doc_ref.id
```

### Decision 7: タイトル前方一致 + タグ検索（フルテキスト検索の代替）

**Rationale**:
- Firestoreはフルテキスト検索をネイティブサポートしていない
- Phase 2では以下の検索方式で代替する:
  - **タイトル前方一致**: `where('title', '>=', prefix).where('title', '<=', prefix + '\uf8ff')`
  - **タグ検索**: `where('tags', 'array_contains', tag)`
- Phase 3でVertex AI Searchを導入し、セマンティック検索を実現予定

**制約**:
- 部分一致検索は不可（"Tips"で"Python Tips"は検索不可）
- 複数タグのAND検索はクライアントサイドフィルタが必要

**検索クエリの判定ロジック**:
```python
if query.startswith('#'):
    # タグ検索: #python → tags array_contains "python"
    tag = query[1:]
    results = await repository.find_by_tags([tag], limit=limit)
else:
    # タイトル前方一致検索
    results = await repository.find_by_title_prefix(query, limit=limit)
```

### Phase 2 アーキテクチャ

```
┌─────────────────┐      HTTPS + Bearer Token      ┌─────────────────┐
│  Claude Code    │ ◄────────────────────────────► │   Cloud Run     │
│  (MCP Client)   │   Authorization: Bearer xxx    │   (FastMCP)     │
│                 │                                │                 │
│  gcloud auth    │                                │  Invoker権限    │
│  print-identity │                                │  で認証         │
│  -token         │                                │                 │
└─────────────────┘                                └────────┬────────┘
                                                            │
                                                            │ ADC (自動)
                                                            ▼
                                                   ┌─────────────────┐
                                                   │   Firestore     │
                                                   │   (Native Mode) │
                                                   └─────────────────┘
```

### Phase 2 ディレクトリ構成（追加分）

```
mcp-server/src/mcp_server/
├── __init__.py
├── main.py
├── models/                      # 追加
│   ├── __init__.py
│   └── knowledge.py             # Knowledgeモデル
├── repositories/                # 追加
│   ├── __init__.py
│   └── knowledge_repository.py  # Firestoreリポジトリ
└── tools/
    ├── __init__.py
    ├── save_knowledge.py        # Firestore保存に変更
    └── search_knowledge.py      # Firestore検索に変更
```

### Phase 2 Open Questions

- [x] Firestore非同期APIの使用方法 → spike/results-phase2.mdで確認済み
- [x] Cloud Run認証方式 → Cloud Run Invoker権限を採用
- [x] フルテキスト検索の代替方法 → タイトル前方一致 + タグ検索
