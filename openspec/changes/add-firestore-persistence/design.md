# Design: Firestore永続化による個人ナレッジの保存・検索

## Context

Phase 2ではナレッジの永続化と検索を実装する。
当初Vertex AI Searchの統合も検討したが、調査の結果：
- FirestoreからのリアルタイムsyncはVertex AI Searchで不可
- 前方一致検索はFirestoreのクエリで十分

## Goals / Non-Goals

### Goals

- ナレッジをFirestoreに永続化
- 前方一致検索の実装
- schema_versionによるスキーマ管理
- Cloud Run Invoker認証の有効化

### Non-Goals

- Vertex AI Searchの統合（将来フェーズ）
- ベクトル検索（将来フェーズ）
- IAP認証（将来のWebダッシュボード向け）

## Decisions

### Decision 1: Cloud Run Invoker + gcloud proxy

**Rationale**:
- Google公式のMCPサーバー向け認証方式
- `gcloud run services proxy`でローカルから安全に接続
- シンプルでセキュア、追加コストなし

**ローカル接続方法**:
```bash
gcloud run services proxy knowledge-mcp-server --region asia-northeast1 --port=3000
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

### Decision 2: Firestore Native mode

**Rationale**:
- ドキュメント指向でナレッジ保存に適合
- リアルタイムリスナーで将来の拡張が容易
- GCPネイティブでCloud Runとの統合がシームレス

**コレクション名**: `knowledge`

**データモデル**:
| フィールド | 型 | 説明 |
|-----------|-----|------|
| id | string | ドキュメントID |
| title | string | ナレッジのタイトル |
| content | string | ナレッジ本文 |
| tags | array | タグのリスト |
| user_id | string | 開発者識別子（Phase 2では固定値 "anonymous"） |
| source | string | personal / team |
| status | string | draft / proposed / promoted |
| path | string | GitHubファイルパス |
| schema_version | number | 初期値: 1 |
| updated_at | timestamp | 最終更新日時 |

### Decision 3: Firestoreクエリによる前方一致検索

**Rationale**:
- Phase 2スコープでは十分な検索精度
- 追加サービス不要でコスト効率が良い
- 将来Vertex AI Searchに移行可能

**制限事項**:
- 前方一致のみ（中間一致・後方一致は不可）
- 複雑なクエリは将来のVertex AI Searchで対応

**検索実装方式**:
- titleフィールドでの前方一致検索
- tagsでのarray-containsフィルタリング

### Decision 4: Repositoryパターンによるインフラ層の抽象化

**Rationale**:
- 将来のデータストア変更時（GCS, Google Drive等）にツール層のコード変更を最小化
- 依存性逆転の原則（DIP）に従い、ドメイン層がインフラ層に依存しない設計
- テスト時にモック実装への差し替えが容易
- 保存・検索を統一的なメンタルモデルで扱える

**データのSSoT整理**:
| ナレッジ種別 | SSoT | 説明 |
|-------------|------|------|
| 個人ナレッジ | Firestore | 開発者個人の断片的なメモ。ライフサイクルが流動的 |
| チームナレッジ | GitHub | チームレビューを経た安定したナレッジ。Firestoreはレプリカ（検索用） |

**設計方針**:
- `domain/` にRepositoryインターフェース（Protocol）を定義
- `infrastructure/` に具体的な実装（Firestore, 将来はGCS/Vertex AI Search等）を配置
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
│  ├─ firestore.py: FirestoreKnowledgeRepository          │
│  ├─ (将来) gcs.py: GCSKnowledgeRepository               │
│  └─ (将来) vertex_ai_search.py: VertexAISearchRepository │
└─────────────────────────────────────────────────────────┘
```

**将来の拡張シナリオ**:
- 検索バックエンド変更: Firestore → Vertex AI Search
- 保存先変更: Firestore → GCS / Google Drive
- 複合構成: 保存はGCS、検索はVertex AI Search（別々のRepository実装）

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
                                                    │ Firestore SDK
                                                    ▼
                                           ┌─────────────────┐
                                           │   Firestore     │
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
    └── firestore.py         # FirestoreKnowledgeRepository
```

### Firestore Python クライアント実装詳細

**依存パッケージ**: `google-cloud-firestore` (v2.22.0)

#### 基本セットアップ

```python
from google.cloud import firestore

client = firestore.Client()
collection = client.collection('knowledge')
```

#### ドキュメント保存

```python
# 自動ID生成で追加
doc_ref = collection.document()
doc_ref.set({
    'title': 'ナレッジタイトル',
    'content': 'ナレッジ本文',
    'user_id': 'user123',
    'source': 'personal',
    'status': 'draft',
    'schema_version': 1,
    'updated_at': firestore.SERVER_TIMESTAMP
})
# doc_ref.id で生成されたIDを取得
```

#### 前方一致検索（Prefix Search）

Firestoreでは前方一致は範囲クエリで実現:

```python
prefix = "Python"
query = (collection
    .where('title', '>=', prefix)
    .where('title', '<', prefix + '\uffff')
    .order_by('title')
    .limit(20))

results = query.get()
for doc in results:
    print(f"{doc.id}: {doc.to_dict()}")
```

#### タグ検索（array-contains）

```python
query = collection.where('tags', 'array_contains', 'python')
```

#### 複合フィルタ（AND/OR）

```python
from google.cloud.firestore_v1.base_query import FieldFilter, Or

query = collection.where(
    filter=Or([
        FieldFilter('status', '==', 'draft'),
        FieldFilter('status', '==', 'proposed')
    ])
)
```

### Repository インターフェース設計

```python
# domain/models.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class Knowledge:
    """ナレッジドメインモデル"""
    id: str
    title: str
    content: str
    tags: list[str] = field(default_factory=list)
    user_id: str = ""
    source: str = "personal"  # 'personal' | 'team'
    status: str = "draft"     # 'draft' | 'proposed' | 'promoted'
    schema_version: int = 1
    updated_at: Optional[datetime] = None
    path: Optional[str] = None
    score: Optional[float] = None  # 検索スコア（Vertex AI Search用、Firestoreでは常にNone）

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
    具体的な実装（Firestore, GCS, Vertex AI Search等）はinfrastructure層で提供。
    """

    def save(self, knowledge: Knowledge) -> Knowledge:
        """ナレッジを保存し、保存されたナレッジ（ID付与済み）を返す

        - id が空の場合は新規作成（IDを自動生成）
        - id が指定されている場合は更新
        - updated_at, schema_version は実装側で自動付与
        """
        ...

    def search(
        self,
        query: str,
        *,
        limit: int = 20,
        offset: int = 0,
    ) -> SearchResult:
        """クエリに一致するナレッジを検索する"""
        ...

    def get(self, id: str) -> Knowledge | None:
        """IDでナレッジを取得する。存在しない場合はNone"""
        ...
```

```python
# infrastructure/firestore.py
from google.cloud import firestore
from ..domain.models import Knowledge, SearchResult
from ..domain.repositories import KnowledgeRepository

class FirestoreKnowledgeRepository(KnowledgeRepository):
    """Firestoreを使用したKnowledgeRepositoryの実装"""

    COLLECTION_NAME = "knowledge"
    SCHEMA_VERSION = 1

    def __init__(self, client: firestore.Client | None = None):
        self._client = client or firestore.Client()
        self._collection = self._client.collection(self.COLLECTION_NAME)

    def save(self, knowledge: Knowledge) -> Knowledge:
        data = {
            "title": knowledge.title,
            "content": knowledge.content,
            "tags": knowledge.tags,
            "user_id": knowledge.user_id,
            "source": knowledge.source,
            "status": knowledge.status,
            "path": knowledge.path,
            "schema_version": self.SCHEMA_VERSION,
            "updated_at": firestore.SERVER_TIMESTAMP,
        }

        if knowledge.id:
            # 更新
            doc_ref = self._collection.document(knowledge.id)
            doc_ref.set(data, merge=True)
        else:
            # 新規作成（ID自動生成）
            doc_ref = self._collection.document()
            doc_ref.set(data)

        # 保存後のドキュメントを取得して返す
        return self._to_knowledge(doc_ref.get())

    def search(
        self,
        query: str,
        *,
        limit: int = 20,
        offset: int = 0,
    ) -> SearchResult:
        # 前方一致検索
        results = (self._collection
            .where("title", ">=", query)
            .where("title", "<", query + "\uffff")
            .order_by("title")
            .limit(limit)
            .offset(offset)
            .get())

        items = [self._to_knowledge(doc) for doc in results]
        return SearchResult(items=items, total=len(items))

    def get(self, id: str) -> Knowledge | None:
        doc = self._collection.document(id).get()
        if not doc.exists:
            return None
        return self._to_knowledge(doc)

    def _to_knowledge(self, doc) -> Knowledge:
        data = doc.to_dict()
        return Knowledge(
            id=doc.id,
            title=data.get("title", ""),
            content=data.get("content", ""),
            tags=data.get("tags", []),
            user_id=data.get("user_id", ""),
            source=data.get("source", "personal"),
            status=data.get("status", "draft"),
            schema_version=data.get("schema_version", 1),
            updated_at=data.get("updated_at"),
            path=data.get("path"),
            score=None,  # Firestoreは検索スコアを返さない
        )
```

## Infrastructure Changes

### GCP API有効化

```bash
gcloud services enable firestore.googleapis.com
```

### Firestoreデータベース作成

```bash
gcloud firestore databases create \
  --database="(default)" \
  --location=asia-northeast1 \
  --type=firestore-native
```

### Cloud Run IAM設定

```bash
PROJECT_ID=$(gcloud config get-value project)
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/datastore.user"
```

### Cloud Run認証設定変更

```bash
gcloud run deploy knowledge-mcp-server \
  --source . \
  --region asia-northeast1 \
  --no-allow-unauthenticated
```

## Risks / Trade-offs

- Firestoreの前方一致検索には中間一致・後方一致の制限あり → 将来Vertex AI Searchで改善予定
- gcloud CLIが必要 → 開発者向けなので許容範囲

## Open Questions

- [x] 認証方式 → Cloud Run Invoker + gcloud proxy
- [x] Firestoreコレクション名 → `knowledge`
