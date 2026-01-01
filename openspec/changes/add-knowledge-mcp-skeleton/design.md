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
- Cloud IAPで認証するため、FastMCP 2.0のエンタープライズ認証機能は不使用

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
- master-plan.mdの「Webhook Endpoint」要件に対応

**Alternatives considered**:
- Cloud Functions: WebSocket/長時間接続に制限があり、MCPプロトコルに不向き
- GKE: 今回の規模ではオーバーエンジニアリング
- Compute Engine: サーバーレスのメリットが得られない

### Decision 3: スタブ実装でスケルトン構築

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
├── tools/
│   ├── __init__.py
│   ├── save_knowledge.py    # save_knowledgeツール
│   └── search_knowledge.py  # search_knowledgeツール
├── Dockerfile
└── requirements.txt

infrastructure/
├── cloudbuild.yaml      # Cloud Build設定
└── terraform/           # Terraform設定（将来）
    └── main.tf
```

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

### Phase 2: ロジック実装（将来）

1. Firestoreデータベース作成
2. `save_knowledge`のFirestore連携
3. `search_knowledge`の基本検索実装

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
