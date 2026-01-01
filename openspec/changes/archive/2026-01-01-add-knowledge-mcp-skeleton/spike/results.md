# 技術検証結果: FastMCP + Cloud Run構成

## 検証項目

知識共有MCPサーバーの垂直スケルトン構築において、FastMCP + Cloud Run構成の技術的妥当性を検証する。

## Context7調査サマリー

### MCP公式Python SDK vs FastMCP 2.0

MCPサーバー実装には2つの選択肢があることが判明した。

#### MCP公式Python SDK (`mcp`)

**ライブラリID**: `/modelcontextprotocol/python-sdk`
**Benchmark Score**: 89.2

- FastMCP 1.0が2024年に統合され、`mcp.server.fastmcp.FastMCP`として利用可能
- MCPプロトコルのコア実装を提供
- `streamable-http`トランスポートをサポート

#### FastMCP 2.0 (`fastmcp`)

**ライブラリID**: `/jlowin/fastmcp`
**Benchmark Score**: 78

- FastMCP 1.0の後継として独立して開発継続
- 公式SDKを超えた本番向け機能を提供：
  - サーバー構成（Composition）、プロキシ
  - OpenAPI/FastAPI生成
  - エンタープライズ認証（Google、GitHub、Azure、Auth0等）
  - デプロイメントツール、テストユーティリティ
- `http`トランスポートをサポート

#### 比較表

| 項目 | MCP公式SDK | FastMCP 2.0 |
|------|-----------|-------------|
| インポート | `from mcp.server.fastmcp import FastMCP` | `from fastmcp import FastMCP` |
| 基本API | `@mcp.tool()` | `@mcp.tool` |
| トランスポート | `streamable-http` | `http` |
| 認証機能 | なし | エンタープライズ対応 |
| サーバー構成 | なし | Composition、Proxy |
| メンテナンス | Anthropic公式 | コミュニティ（活発） |
| 将来の破壊的変更 | 不明 | 3.0で予定（`fastmcp<3`でピン留め推奨） |

#### 結論：FastMCP 2.0を採用

**理由：**

1. **基本APIは同一**: インポートパス以外は公式SDKと同じ使い方
2. **追加機能は使わなければ影響しない**: 認証やCompositionは明示的に有効化しない限り無効
3. **将来の移行不要**: Phase 2以降で認証機能が必要になっても移行作業なし
4. **活発なメンテナンス**: 公式SDKより更新頻度が高い
5. **本番向けドキュメント充実**: デプロイメントのベストプラクティスが豊富

**注意事項：**
- `fastmcp<3`でバージョンをピン留め（3.0で破壊的変更予定）
- Cloud IAPで認証するため、FastMCP 2.0のエンタープライズ認証機能は不使用

---

### FastMCP 2.0の詳細

**主要な発見**:

1. **HTTPトランスポート対応**: FastMCPはHTTPトランスポートをネイティブサポートしており、Cloud Runでのホスティングに適している
2. **FastAPI統合**: 既存のFastAPIアプリケーションにMCPサーバーをマウント可能（`api.mount("/mcp", mcp.http_app())`）
3. **ヘルスチェック**: `@mcp.custom_route`デコレータでカスタムHTTPエンドポイント（`/health`）を追加可能
4. **ツール定義**: `@mcp.tool`デコレータでPython関数をMCPツールとして登録。型ヒントから自動的にJSONスキーマを生成

**コード例（調査結果）**:

```python
from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import PlainTextResponse

mcp = FastMCP("MyServer")

@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> PlainTextResponse:
    return PlainTextResponse("OK")

@mcp.tool
def save_knowledge(title: str, content: str) -> str:
    """ナレッジを保存する"""
    return f"Saved: {title}"

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8080)
```

### FastMCP 2.0 トランスポート選択肢

FastMCP 2.0は3つのトランスポートプロトコルをサポートする。

#### 1. STDIO（デフォルト）

```python
mcp.run()  # or mcp.run(transport="stdio")
```

- **用途**: ローカルCLI統合、コマンドラインスクリプト
- **特徴**: 1プロセス1クライアント
- **Cloud Run適性**: ❌ 不適（Webサービス向けではない）

#### 2. HTTP（Streamable HTTP）- 推奨

```python
mcp.run(transport="http", host="0.0.0.0", port=8000)
```

- **用途**: Webデプロイメント、ネットワーク経由のアクセス
- **特徴**:
  - 双方向ストリーミング対応（Streamable HTTPプロトコル）
  - 複数クライアント同時接続可能
  - `stateless_http=True`でステートレスモード（水平スケーリング向け）
- **Cloud Run適性**: ✅ 推奨

#### 3. SSE（Server-Sent Events）- レガシー

```python
mcp.run(transport="sse", host="127.0.0.1", port=8080)
```

- **用途**: 後方互換性
- **特徴**: Streamable HTTPに置き換えられた
- **Cloud Run適性**: △ 非推奨（新規デプロイにはHTTPを使用）

#### トランスポート比較表

| トランスポート | 用途 | 複数クライアント | ステートレス | Cloud Run |
|---------------|------|-----------------|-------------|-----------|
| STDIO | ローカルCLI | ❌ | - | ❌ |
| HTTP | Webデプロイ | ✅ | ✅ (`stateless_http=True`) | ✅ 推奨 |
| SSE | レガシー互換 | ✅ | - | △ |

#### 結論：HTTPトランスポート + ステートレスモードを採用

```python
# Cloud Run最適化設定
mcp = FastMCP("KnowledgeGateway", stateless_http=True)
```

**理由**:
- 水平スケーリング対応（セッションアフィニティ不要）
- Cloud Runの複数インスタンスに対応
- 双方向ストリーミングでMCPプロトコルの全機能をサポート

---

### Cloud Run との相性分析

**ライブラリID**: `/googlecloudplatform/cloud-run-samples`

#### Cloud Runの特徴

1. **コンテナポート**: デフォルトでポート8080を期待
2. **ヘルスチェック**: `startupProbe`でTCPソケットベースのヘルスチェック設定可能
3. **環境変数**: `PORT`環境変数でポートを動的に設定可能
4. **認証**: IAMベースのアクセス制御、または`allUsers`で公開アクセス可能

#### FastMCP HTTP + Cloud Run 相性評価

| 観点 | 評価 | 詳細 |
|------|------|------|
| ステートレス対応 | ✅ | `stateless_http=True`でセッションアフィニティ不要 |
| 水平スケーリング | ✅ | ステートレスモードで複数インスタンス対応 |
| コールドスタート | ✅ | HTTPリクエストベースで問題なし |
| ヘルスチェック | ✅ | `@mcp.custom_route("/health")`で対応 |
| カスタムエンドポイント | ✅ | Webhook用`POST /sync`等も追加可能 |
| ポート設定 | ✅ | `PORT`環境変数対応 |

---

### ロードマップとの整合性確認

`docs/roadmap.md`の要件との整合性を検証した。

#### Phase 1（現在）: 垂直スケルトンの構築

| 要件 | 対応状況 | 備考 |
|------|----------|------|
| MCP Server (Knowledge Gateway) on Cloud Run | ✅ | FastMCP 2.0 + HTTPトランスポート |
| Local Agent (Claude Code) からMCP経由でアクセス | ✅ | HTTPトランスポートで対応 |
| ヘルスチェックエンドポイント | ✅ | `@mcp.custom_route("/health")` |

#### Phase 2: 個人ナレッジの永続化と検索

| 要件 | 対応状況 | 備考 |
|------|----------|------|
| Firestoreデータモデリング | ✅ 対応可能 | MCPツールからFirestore SDK呼び出し |
| Vertex AI Search統合 | ✅ 対応可能 | MCPツールから呼び出し |

#### Phase 3: Remote Agent による知的自動化

| 要件 | 対応状況 | 備考 |
|------|----------|------|
| Remote Knowledge Agent (Vertex AI Agent Engine) | ✅ 対応可能 | MCP経由でアクセス |
| 高度なナレッジ操作ツール追加 | ✅ 対応可能 | `@mcp.tool`で追加 |

#### Phase 4: チーム共有と同期メカニズム（重要）

| 要件 | 対応状況 | 備考 |
|------|----------|------|
| **Webhook Endpoint** (`POST /sync`) | ✅ 対応可能 | `@mcp.custom_route("/sync", methods=["POST"])` |
| GitHub Actions からの同期リクエスト受付 | ✅ 対応可能 | カスタムルートでHTTP POST処理 |
| Markdown パースしてFirestoreへ書き込み | ✅ 対応可能 | Webhook内で実装 |

#### Phase 4対応コード例

```python
from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse

mcp = FastMCP("KnowledgeGateway", stateless_http=True)

# Phase 4: GitHub Actions同期用エンドポイント
@mcp.custom_route("/sync", methods=["POST"])
async def sync_from_github(request: Request) -> JSONResponse:
    """GitHub Actionsからの同期リクエストを受け付ける"""
    data = await request.json()
    # Markdownをパースしてfirestoreへ書き込み
    # ...
    return JSONResponse({"status": "synced", "count": len(data.get("files", []))})
```

#### 整合性結論

**FastMCP 2.0 + HTTPトランスポート + Cloud Run構成は、ロードマップの全Phaseに対応可能。**

特にPhase 4の「Webhook Endpoint」要件は`@mcp.custom_route`で完全に対応できる。

## 技術的妥当性の評価

### 評価項目

| 項目 | 評価 | 備考 |
|------|------|------|
| HTTPトランスポート | ✅ 対応 | FastMCPネイティブサポート |
| ヘルスチェック | ✅ 対応 | `@mcp.custom_route`で実装可能 |
| FastAPI統合 | ✅ 対応 | `mcp.http_app()`でマウント可能 |
| Cloud Run互換性 | ✅ 対応 | 標準的なHTTPサーバーとしてデプロイ可能 |
| ツール定義 | ✅ シンプル | デコレータベースで直感的 |
| スキーマ生成 | ✅ 自動 | 型ヒントから自動生成 |

### 懸念事項と対策

1. **MCPプロトコルのHTTPマッピング**
   - FastMCPは内部でHTTPトランスポートを処理
   - クライアント側はHTTP経由でMCPプロトコルを使用

2. **認証**
   - Phase 1では認証なし（開発用途）
   - 将来的にはCloud IAP（ロードバランサー不要でCloud Runに直接設定可能）を使用

## 推奨構成

### アーキテクチャ

```
┌─────────────────┐      HTTPS      ┌─────────────────┐
│  Claude Code    │ ◄──────────────► │   Cloud Run     │
│  (MCP Client)   │                  │   (FastMCP)     │
└─────────────────┘                  └────────┬────────┘
                                              │
                                              ▼
                                     ┌─────────────────┐
                                     │   Firestore     │
                                     │   (Phase 2)     │
                                     └─────────────────┘
```

### ディレクトリ構成

```
src/mcp_server/
├── __init__.py
├── main.py              # FastMCPサーバーエントリポイント
└── tools/
    ├── __init__.py
    ├── save_knowledge.py
    └── search_knowledge.py

pyproject.toml           # プロジェクトメタデータ・依存関係
uv.lock                  # 依存関係ロックファイル（自動生成）
Procfile                 # Buildpacks用エントリポイント定義
```

**注**: Google Cloud BuildpacksがuvをGAでサポート。`pyproject.toml` + `uv.lock`を自動検出してビルドするため、Dockerfileは不要。

### スケルトン実装（Phase 1）

```python
# src/mcp_server/main.py
import os
from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import PlainTextResponse

# ステートレスモードでCloud Run最適化
mcp = FastMCP("KnowledgeGateway", stateless_http=True)

@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> PlainTextResponse:
    return PlainTextResponse("OK")

@mcp.tool
def save_knowledge(title: str, content: str, tags: list[str] = []) -> dict:
    """ナレッジを保存する（スタブ実装）"""
    return {"status": "saved", "id": "stub-id", "title": title}

@mcp.tool
def search_knowledge(query: str, limit: int = 10) -> list[dict]:
    """ナレッジを検索する（スタブ実装）"""
    return [{"id": "stub-id", "title": "Sample Knowledge", "score": 0.95}]

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    mcp.run(transport="http", host="0.0.0.0", port=port)
```

## 結論

**FastMCP + Cloud Run構成は技術的に妥当であり、採用を推奨する。**

理由:
- FastMCPはHTTPトランスポートをネイティブサポートしており、Cloud Runとの相性が良い
- デコレータベースのAPI設計により、ツール定義が直感的
- ヘルスチェックエンドポイントの追加が容易
- 型ヒントからの自動スキーマ生成により、開発効率が高い

## 次のステップ

1. ~~技術検証完了~~ ✅
2. ~~design.md作成~~ ✅（当初不要と判断したが、Open Questionsの整理のため作成）
3. verify.md作成（Runme.dev形式）
4. スケルトン実装開始
