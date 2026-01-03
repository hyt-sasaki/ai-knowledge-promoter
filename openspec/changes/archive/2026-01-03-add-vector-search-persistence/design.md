# Design: Vector Search 2.0による個人ナレッジの永続化と検索

## Context

Phase 2ではナレッジの永続化と検索を実装する。
当初Firestoreを検討したが、Vertex AI Vector Search 2.0の調査により設計を変更：

- Vector Search 2.0はドキュメントとベクトルを統合管理
- Auto-Embeddingsで手動ベクトル化が不要
- セマンティック検索が最初から使える（Phase 2.5が不要に）
- Public Preview中は無料で実験的プロジェクトに適合

## Goals / Non-Goals

### Goals

- ナレッジをVector Search 2.0 Collectionに永続化
- セマンティック検索の実装
- Cloud Run Invoker認証の有効化

### Non-Goals

- ハイブリッド検索の最適化（将来フェーズ）
- フィールド別検索（tags, title等でのフィルタリング）（将来フェーズ）
- IAP認証（将来のWebダッシュボード向け）
- マルチユーザー対応（Phase 3で実装）

## Decisions

### Decision 1: Cloud Run Invoker + gcloud proxy

**Rationale**:
- Google公式のMCPサーバー向け認証方式
- `gcloud run services proxy`でローカルから安全に接続
- シンプルでセキュア、追加コストなし

**ローカル接続方法**:
```bash
gcloud run services proxy knowledge-mcp-server --region us-central1 --port=3000
```

**Claude Code MCP設定**:
```json
{
  "mcpServers": {
    "knowledge-gateway": {
      "url": "http://localhost:3000/mcp"
    }
  }
}
```

**Alternatives considered**:
- IAP: Webダッシュボード向け。MCPクライアントには複雑すぎる
- allUsers（認証なし）: 実データを扱うPhase 2では不適切

### Decision 2: Vertex AI Vector Search 2.0

**Rationale**:
- ドキュメントとベクトルを統合管理（別途Firestore不要）
- Auto-Embeddingsで開発効率向上
- セマンティック検索 + 全文検索のハイブリッド検索が可能
- インフラ自動管理でシャード・レプリカ設定不要
- Public Preview中は無料

**Collection名**: `knowledge`

**データモデル（data_schema）**:
| フィールド | 型 | 説明 |
|-----------|-----|------|
| id | string | ドキュメントID |
| title | string | ナレッジのタイトル |
| content | string | ナレッジ本文 |
| tags | array | タグのリスト |
| user_id | string | 開発者識別子（Phase 2では固定値 "anonymous"） |
| source | string | personal / team |
| status | string | draft / proposed / promoted |
| github_path | string | GitHubファイルパス（team/promotedのみ） |
| pr_url | string | 昇格PR URL（personal/proposedのみ） |
| promoted_from_id | string | 昇格元ナレッジID（team/promotedのみ） |
| created_at | string | 作成日時（ISO 8601） |
| updated_at | string | 更新日時（ISO 8601） |

**フィールド補足**:
- `github_path`: 旧 `path` をリネーム。team/promotedナレッジのGitHubファイルパス。個人ナレッジでは空文字列。
- `pr_url`: 昇格PRのURL。personal/proposedの間のみ設定。
- `promoted_from_id`: 昇格元の個人ナレッジID。team/promotedナレッジで設定。GitHub直接作成の場合は空文字列。
- `created_at` / `updated_at`: ISO 8601形式の文字列（例: `"2026-01-02T15:30:00Z"`）を採用。型選択の詳細は後述の「時刻フィールドの型選択」を参照。

**有効な状態の組み合わせ**:
| source | status | github_path | pr_url | promoted_from_id | 説明 |
|--------|--------|-------------|--------|------------------|------|
| personal | draft | "" | "" | "" | 個人の下書き |
| personal | proposed | "" | PR URL | "" | 昇格PR作成済み |
| team | promoted | ファイルパス | "" | 元ID | 昇格済み（個人から） |
| team | promoted | ファイルパス | "" | "" | GitHub直接作成 |

**時刻フィールドの型選択（created_at / updated_at）**:

| 観点 | Unix時間（number） | ISO 8601（string） |
|------|-------------------|-------------------|
| ソート効率 | ✅ 数値比較で高速 | ⚠️ 辞書順ソートは可能だが数値より低速 |
| 範囲検索 | ✅ `> 1704067200` のような数値比較が可能 | ⚠️ 文字列比較が必要 |
| 可読性 | ❌ `1704067200` は人間が読めない | ✅ `2024-01-01T00:00:00Z` は直感的 |
| デバッグ | ❌ 変換が必要 | ✅ そのまま確認可能 |
| タイムゾーン | ✅ UTCとして一意 | ✅ `Z` サフィックスでUTC明示 |
| 精度 | ⚠️ 秒精度（ミリ秒は小数点） | ✅ ISO 8601はミリ秒まで標準対応 |
| Vector Search 2.0対応 | ✅ `number`型で格納可能 | ✅ `string`型で格納可能 |

**用途**:
1. 監査・デバッグ: ナレッジがいつ作成・更新されたかの追跡
2. 将来のソート・フィルタ: 「最近保存したナレッジ」の取得（Phase 2では未実装）
3. 同期判定: GitHub連携時に更新が必要かの判定

**採用**: ISO 8601（string）

**Rationale**:
- Phase 2の主要用途は監査・デバッグであり、可読性を優先
- ソート・フィルタ機能はNon-Goals（将来フェーズで対応）
- ISO 8601は辞書順ソートが可能で、将来の範囲検索にも最低限対応可能
- スキーマ変更が困難なため、将来Unix時間が必要になった場合は新フィールド追加またはCollection移行で対応

**ナレッジステータス遷移**:
```
┌──────────────────────────────────────────────────────────────────────┐
│  個人ナレッジの昇格フロー                                              │
│                                                                      │
│  (personal, draft) ──► (personal, proposed)                          │
│                         pr_url=PR URL                                │
│                              │                                       │
│                              │ PR マージ                             │
│                              ▼                                       │
│    ┌─────────────────────────┴─────────────────────┐                 │
│    ▼                                               ▼                 │
│  archived_knowledge に移動              knowledge に新規作成          │
│  (promoted_to_id=新ID)                  (team, promoted)             │
│                                         (promoted_from_id=元ID)       │
│                                         (github_path=ファイルパス)    │
├──────────────────────────────────────────────────────────────────────┤
│  GitHub 直接作成                                                      │
│                                                                      │
│  GitHub Actions → (team, promoted, promoted_from_id="")              │
└──────────────────────────────────────────────────────────────────────┘
```

- **draft**: 保存直後の初期状態。開発者個人の断片的なメモ
- **proposed**: Remote Agentが昇格PRを作成した状態。pr_urlにPR URLを保持
- **promoted**: PRマージ後のチームナレッジ。github_pathにファイルパスを保持

**アーカイブ方式**:

論理削除（status: archived）は「WHERE句地獄」問題を引き起こすため、
アーカイブ専用コレクション `archived_knowledge` を採用：

```
┌─────────────────────────────────────────────────────────────────┐
│  knowledge コレクション（アクティブなデータのみ）                    │
│  - personal/draft, personal/proposed, team/promoted             │
│                                                                 │
│  delete_knowledge → 物理削除（完全消去）                          │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  archived_knowledge コレクション（昇格済み元ナレッジ）              │
│  - 昇格完了時に元ナレッジをここに移動                              │
│  - promoted_to_id で新ナレッジを参照                             │
│  - 検索対象外、追跡・監査用途                                     │
└─────────────────────────────────────────────────────────────────┘
```

**メリット**:
1. 検索がシンプル（knowledge コレクションはアクティブなもののみ）
2. delete と archive の意味が明確（削除は消去、アーカイブは保管）
3. WHERE句地獄回避（status != 'archived' が不要）

**ArchivedKnowledge モデル**（Phase 3/4で実装）:
| フィールド | 型 | 説明 |
|-----------|-----|------|
| id | string | 元のナレッジID |
| title | string | タイトル |
| content | string | 本文 |
| tags | array | タグ |
| user_id | string | 作成者 |
| promoted_to_id | string | 昇格先のナレッジID |
| archived_at | string | アーカイブ日時（ISO 8601） |
| original_created_at | string | 元の作成日時（ISO 8601） |

**ベクトルスキーマ（vector_schema）**:
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

※ gemini-embedding-001はデフォルトで3072次元を出力する。768次元はMRL（Matryoshka Representation Learning）による縮小次元で、ストレージコストと検索性能のバランスを考慮して選択。

### Decision 3: セマンティック検索をデフォルトに

**Rationale**:
- ナレッジ検索はキーワード一致より意味的な関連性が重要
- Auto-Embeddingsで追加コストなくセマンティック検索が可能
- 将来的にハイブリッド検索への拡張も容易

**検索実装方式**:
- セマンティック検索（デフォルト）
- 全文検索（オプション、将来実装）
- ハイブリッド検索（オプション、将来実装）

### Decision 4: Repositoryパターンによるインフラ層の抽象化

**Rationale**:
- 将来のデータストア変更時にツール層のコード変更を最小化
- 依存性逆転の原則（DIP）に従い、ドメイン層がインフラ層に依存しない設計
- テスト時にモック実装への差し替えが容易
- 保存・検索を統一的なメンタルモデルで扱える

**データのSSoT整理**:
| ナレッジ種別 | SSoT | 説明 |
|-------------|------|------|
| 個人ナレッジ | Vector Search 2.0 | 開発者個人の断片的なメモ。ライフサイクルが流動的 |
| チームナレッジ | GitHub | チームレビューを経た安定したナレッジ。Vector Searchはレプリカ（検索用） |

**設計方針**:
- `domain/` にRepositoryインターフェース（Protocol）を定義
- `infrastructure/` に具体的な実装を配置
- ツール層はインターフェースにのみ依存し、DIで具体実装を注入
- 保存（save）と検索（search）の両方をRepositoryで抽象化

**レイヤー構成**:
```
┌─────────────────────────────────────────────────────────┐
│  Tools Layer (save_knowledge.py, search_knowledge.py)   │
│  → KnowledgeRepositoryインターフェースに依存              │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼ 依存性注入
┌─────────────────────────────────────────────────────────┐
│  Domain Layer (domain/repositories.py)                  │
│  → KnowledgeRepository Protocol定義                     │
│  → Knowledge dataclass定義                              │
└─────────────────────────────────────────────────────────┘
                          ▲
                          │ 実装
┌─────────────────────────────────────────────────────────┐
│  Infrastructure Layer                                   │
│  └─ vector_search.py: VectorSearchKnowledgeRepository   │
└─────────────────────────────────────────────────────────┘
```

### Decision 5: Collection作成方式（ローカルスクリプト）

**Rationale**:
- Collection作成は初回1回のみ必要な操作
- setupエンドポイントを用意すると認証の複雑化を招く
- 開発者がローカルで手動実行する方がシンプル

**実装方式**:
- `scripts/create_collection.py` としてPythonスクリプトを用意
- 開発者がgcloud認証済みの状態でローカル実行
- 冪等性を持たせ、既存Collectionがあればスキップ

**実行手順**:
```bash
# 1. gcloud認証
gcloud auth application-default login

# 2. Collection作成
python scripts/create_collection.py
```

**Alternatives considered**:
- setupエンドポイント: Cloud Run認証の複雑化。MCPクライアントからの呼び出しが煩雑
- Terraform/gcloud CLI: Vector Search 2.0はPython SDKでの操作が前提

## Architecture

### システム構成図（Phase 2）

```
┌─────────────────┐      gcloud proxy      ┌─────────────────┐
│  Claude Code    │ ◄────────────────────► │   Cloud Run     │
│  (MCP Client)   │   localhost:3000       │   (FastMCP)     │
│                 │                        │                 │
│  .claude/       │                        │  /health (GET)  │
│  mcp_servers.json                        │  /mcp (MCP)     │
└─────────────────┘                        └────────┬────────┘
                                                    │
                                                    │ Vector Search SDK
                                                    ▼
                                           ┌─────────────────┐
                                           │  Vector Search  │
                                           │  2.0 Collection │
                                           │   (knowledge)   │
                                           └─────────────────┘
```

### ディレクトリ構成

```
mcp-server/src/mcp_server/
├── __init__.py
├── main.py
├── tools/
│   ├── __init__.py
│   ├── save_knowledge.py    # Repository経由で保存
│   └── search_knowledge.py  # Repository経由で検索
├── domain/                  # 新規: ドメイン層
│   ├── __init__.py
│   ├── models.py            # Knowledge dataclass
│   └── repositories.py      # KnowledgeRepository Protocol
└── infrastructure/          # 新規: インフラ層
    ├── __init__.py
    └── vector_search.py     # VectorSearchKnowledgeRepository
```

### Vector Search 2.0 Python クライアント実装詳細

**依存パッケージ**: `google-cloud-vectorsearch`

#### 基本セットアップ

```python
from google.cloud import vectorsearch_v1beta

vector_search_service_client = vectorsearch_v1beta.VectorSearchServiceClient()
data_object_service_client = vectorsearch_v1beta.DataObjectServiceClient()
data_object_search_service_client = vectorsearch_v1beta.DataObjectSearchServiceClient()
```

#### Collection作成

```python
request = vectorsearch_v1beta.CreateCollectionRequest(
    parent=f"projects/{PROJECT_ID}/locations/{LOCATION}",
    collection_id="knowledge",
    collection={
        "data_schema": {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "title": {"type": "string"},
                "content": {"type": "string"},
                "tags": {"type": "array", "items": {"type": "string"}},
                "user_id": {"type": "string"},
                "source": {"type": "string"},
                "status": {"type": "string"},
                "github_path": {"type": "string"},
                "pr_url": {"type": "string"},
                "promoted_from_id": {"type": "string"},
                "created_at": {"type": "string"},
                "updated_at": {"type": "string"},
            },
        },
        "vector_schema": {
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
        },
    },
)
operation = vector_search_service_client.create_collection(request=request)
operation.result()
```

#### ドキュメント保存

```python
request = vectorsearch_v1beta.CreateDataObjectRequest(
    parent=f"projects/{PROJECT_ID}/locations/{LOCATION}/collections/knowledge",
    data_object_id=knowledge_id,
    data_object={
        "data": {
            "id": knowledge_id,
            "title": title,
            "content": content,
            "tags": tags,
            "user_id": user_id,
            "source": source,
            "status": status,
            "github_path": github_path,
            "pr_url": pr_url,
            "promoted_from_id": promoted_from_id,
            "created_at": created_at,
            "updated_at": updated_at,
        },
        "vectors": {},  # Auto-Embeddings
    },
)
data_object_service_client.create_data_object(request=request)
```

#### セマンティック検索

```python
request = vectorsearch_v1beta.SearchDataObjectsRequest(
    parent=f"projects/{PROJECT_ID}/locations/{LOCATION}/collections/knowledge",
    semantic_search=vectorsearch_v1beta.SemanticSearch(
        search_text=query,
        search_field="content_embedding",
        task_type="QUESTION_ANSWERING",
        top_k=20,
        output_fields=vectorsearch_v1beta.OutputFields(
            data_fields=["id", "title", "content", "tags", "user_id", "source", "status"]
        ),
    ),
)
results = data_object_search_service_client.search_data_objects(request)
```

### Repository インターフェース設計

```python
# domain/models.py
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Knowledge:
    """ナレッジドメインモデル"""
    id: str
    title: str
    content: str
    tags: list[str] = field(default_factory=list)
    user_id: str = "anonymous"

    # ライフサイクル管理
    source: str = "personal"  # 'personal' | 'team'
    status: str = "draft"     # 'draft' | 'proposed' | 'promoted'

    # GitHub 連携
    github_path: str = ""       # GitHubファイルパス（team/promotedのみ）
    pr_url: str = ""            # 昇格PR URL（personal/proposedのみ）
    promoted_from_id: str = ""  # 昇格元ID（team/promotedのみ）

    # タイムスタンプ
    created_at: datetime | None = None
    updated_at: datetime | None = None

    # 検索専用
    score: float | None = None

@dataclass
class SearchResult:
    """検索結果"""
    items: list[Knowledge]
    total: int
```

```python
# domain/repositories.py
from typing import Protocol
from .models import Knowledge, SearchResult

class KnowledgeRepository(Protocol):
    """ナレッジの保存・検索のためのリポジトリインターフェース

    依存性逆転の原則（DIP）に基づき、ツール層はこのインターフェースに依存する。
    具体的な実装はinfrastructure層で提供。
    """

    def save(self, knowledge: Knowledge) -> Knowledge:
        """ナレッジを保存し、保存されたナレッジ（ID付与済み）を返す

        - id が空の場合は新規作成（IDを自動生成）
        - id が指定されている場合は更新
        - created_at, updated_at は実装側で自動付与
        """
        ...

    def search(
        self,
        query: str,
        *,
        limit: int = 20,
    ) -> SearchResult:
        """クエリに一致するナレッジをセマンティック検索する"""
        ...

    def get(self, id: str) -> Knowledge | None:
        """IDでナレッジを取得する。存在しない場合はNone"""
        ...

    def delete(self, id: str) -> bool:
        """IDでナレッジを削除する。削除成功時はTrue、存在しない場合はFalse"""
        ...
```

## Infrastructure Changes

### GCP API有効化

```bash
gcloud services enable vectorsearch.googleapis.com aiplatform.googleapis.com \
    --project "{PROJECT_ID}"
```

### Cloud Run IAM設定

```bash
PROJECT_ID=$(gcloud config get-value project)
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")

# Vector Search関連の権限を付与（要確認）
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/aiplatform.user"
```

### Cloud Run認証設定変更

```bash
gcloud run deploy knowledge-mcp-server \
  --source . \
  --region us-central1 \
  --no-allow-unauthenticated
```

## Risks / Trade-offs

- Vector Search 2.0はPublic Preview → GA時にAPI変更の可能性あり
- リージョン制限（us-central1がデフォルト、asia-northeast1は要確認）
- gcloud CLIが必要 → 開発者向けなので許容範囲
- **スキーマ変更制約**: Collectionのスキーマ（data_schema, vector_schema）は作成後の変更が困難
  - 公式ドキュメントにUpdateCollection APIは確認できず
  - `additionalProperties`は常に`false`として扱われる厳格なスキーマ検証
  - **マイグレーション戦略**: 将来のフィールド追加（ハイブリッド検索等）が必要な場合は、新Collectionを作成しデータ移行
  - Repositoryパターン採用により移行コストは軽減される

## Open Questions

- [x] 認証方式 → Cloud Run Invoker + gcloud proxy
- [x] データストア → Vector Search 2.0
- [x] リージョン → us-central1を使用（公式ドキュメントで確認済み。asia-northeast1は未確認だが、us-central1で問題なし）
- [x] IAM権限 → roles/aiplatform.userで十分（Cloud RunサービスアカウントがVector Searchと連携するのに必要な権限を含む）

## 参考リンク

- [Vertex AI Vector Search 2.0 紹介記事](https://zenn.dev/google_cloud_jp/articles/vector-search-2-0-intro)
- [Vector Search 2.0 APIs](https://docs.cloud.google.com/vertex-ai/docs/vector-search-2/api/api)
- [公式サンプルノートブック](https://github.com/GoogleCloudPlatform/generative-ai/blob/aa78d593935ab75a1d5a6ca96d6716076b898d62/embeddings/vector-search-2-intro.ipynb)
