# 技術検証結果: Phase 2（Firestore + Cloud Run認証）

## 検証項目

Phase 2実装に向けたFirestore連携とCloud Run認証の技術検証を実施した。

## 1. Firestore Python SDK

### 1.1 非同期API（AsyncClient）

**ライブラリ**: `google-cloud-firestore>=2.14.0`

Firestore Python SDKは非同期APIをネイティブサポートしている。`AsyncClient`を使用することで、FastMCPの非同期ツールと統合可能。

```python
from google.cloud import firestore

async def async_operations():
    # 非同期クライアント作成
    client = firestore.AsyncClient()

    try:
        # ドキュメント作成
        doc_ref = client.document('knowledge', 'doc123')
        await doc_ref.set({
            'title': 'Test Knowledge',
            'content': 'Test content',
            'tags': ['python', 'test'],
            'status': 'draft',
            'schema_version': 1,
            'created_at': firestore.SERVER_TIMESTAMP,
            'updated_at': firestore.SERVER_TIMESTAMP,
        })

        # ドキュメント読み取り
        snapshot = await doc_ref.get()
        if snapshot.exists:
            data = snapshot.to_dict()

        # クエリ実行
        collection = client.collection('knowledge')
        query = collection.where('status', '==', 'draft').limit(10)
        async for doc in query.stream():
            print(f"Found: {doc.id}")

    finally:
        await client.close()
```

**Cloud Run上でのデフォルト認証**:
- Cloud Runサービスは自動的にサービスアカウントの認証情報を使用
- `AsyncClient()`の引数なしで初期化可能（Application Default Credentials）
- 追加の認証設定は不要

### 1.2 array_contains検索（タグ検索）

タグ検索には`array_contains`演算子を使用する。

```python
# 単一タグ検索
query = collection.where('tags', 'array_contains', 'python')
results = await query.get()

# 複数タグのいずれかにマッチ（array_contains_any）
query = collection.where('tags', 'array_contains_any', ['python', 'javascript'])
results = await query.get()
```

**制約**:
- `array_contains`は1クエリにつき1つのみ使用可能
- 複数タグのAND検索はクライアントサイドフィルタが必要

### 1.3 タイトル前方一致検索（フルテキスト検索の代替）

Firestoreはフルテキスト検索をネイティブサポートしていないため、前方一致検索で代替する。

```python
# タイトル前方一致検索
prefix = "Python"
query = collection \
    .where('title', '>=', prefix) \
    .where('title', '<=', prefix + '\uf8ff') \
    .limit(10)
results = await query.get()
```

**仕組み**:
- `\uf8ff`はUnicodeの最後の文字に近く、前方一致検索を実現
- 例: `title >= "Python"` AND `title <= "Python\uf8ff"` → "Python Tips", "Python入門" などがマッチ

**制約**:
- 部分一致検索は不可（"Tips"で"Python Tips"は検索不可）
- 大文字小文字を区別する（正規化が必要な場合は別フィールドを用意）

### 1.4 複合フィルタ（AND/OR）

```python
from google.cloud.firestore_v1.base_query import FieldFilter, And, Or

# OR検索
query = collection.where(
    filter=Or([
        FieldFilter('status', '==', 'draft'),
        FieldFilter('status', '==', 'proposed'),
    ])
)

# AND検索（複数条件）
query = collection.where(
    filter=And([
        FieldFilter('source', '==', 'personal'),
        FieldFilter('status', '==', 'draft'),
    ])
)
```

---

## 2. Cloud Run認証

### 2.1 認証方式の選択

調査の結果、2つの認証方式が利用可能であることが判明した。

| 方式 | 概要 | 利点 | 欠点 |
|------|------|------|------|
| **Cloud Run Invoker権限** | `roles/run.invoker`で認証 | シンプル、追加コストなし、proxyでトークン管理不要 | - |
| **Cloud IAP** | Identity-Aware Proxyで認証 | ユーザー認証、監査ログ充実、組織なしでも利用可能 | ベータ版 |

**結論**: Phase 2では**Cloud Run Invoker権限**を採用する。

**理由**:
1. Cloud Run Invoker権限はシンプルで十分なセキュリティを提供
2. `gcloud run services proxy`を使用することでトークン管理が不要
3. 将来的にCloud IAPへの移行も容易
4. Cloud IAPはCloud Run直接統合がベータ版（`gcloud beta run deploy --iap`）

**Cloud IAPについての補足**:
- Gmailアカウントでも利用可能（組織なしでOK）。[Google Codelabs](https://codelabs.developers.google.com/secure-serverless-application-with-identity-aware-proxy?hl=ja#1)参照
- Cloud IAPのCloud Run直接統合はベータ版
- 将来的にCloud IAPへの移行も選択肢として残す

### 2.2 Cloud Run Invoker権限の設定

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

### 2.3 Claude Codeからの認証方法

ローカルのMCPクライアント（Claude Code）からCloud Run上のMCPサーバーに接続する方法は複数ある。

#### 方法1: gcloud run services proxy（推奨）

[Google公式ドキュメント](https://docs.cloud.google.com/run/docs/host-mcp-servers)で推奨されている方法。ローカルにプロキシを立て、自動的にIDトークンを注入する。

```bash
# ローカルプロキシを起動（ポート3000でリッスン）
gcloud run services proxy knowledge-mcp-server --region asia-northeast1 --port=3000
```

**利点**:
- トークン管理が不要（自動的にIDトークンを注入）
- トークンの期限切れを気にする必要がない
- セキュアな接続（ローカルからCloud Runへのリクエストを安全に転送）

**MCP設定**:
```json
{
  "mcpServers": {
    "knowledge-gateway": {
      "url": "http://localhost:3000/mcp"
    }
  }
}
```

**制約**:
- プロキシプロセスを常時起動しておく必要がある
- Claude Code起動前にプロキシを開始する必要がある

#### 方法2: IDトークンを直接指定

一時的なテストや自動化スクリプトで使用する場合。

```bash
# IDトークンを取得（1時間で期限切れ）
TOKEN=$(gcloud auth print-identity-token)

# Claude CodeにMCPサーバーを追加
claude mcp add --transport http knowledge-gateway \
  https://knowledge-mcp-server-xxxxx.run.app/mcp \
  --header "Authorization: Bearer ${TOKEN}"
```

**注意点**:
- `gcloud auth print-identity-token`で取得したトークンは**1時間で期限切れ**
- 長期利用には不向き
- テストやデバッグ用途に限定

#### 推奨: 方法1（gcloud run services proxy）

開発中は`gcloud run services proxy`を使用することを推奨する。トークン管理の手間がなく、セキュアな接続が可能。

---

## 3. 推奨構成

### 3.1 Phase 2の認証構成

```
┌─────────────────┐                                ┌─────────────────┐
│  Claude Code    │                                │   Cloud Run     │
│  (MCP Client)   │                                │   (FastMCP)     │
│                 │                                │                 │
│  localhost:3000 │──────► gcloud run ────────────►│  Invoker権限    │
│  /mcp           │        services proxy          │  で認証         │
│                 │        (トークン自動注入)       │                 │
└─────────────────┘                                └────────┬────────┘
                                                            │
                                                            │ ADC (自動)
                                                            ▼
                                                   ┌─────────────────┐
                                                   │   Firestore     │
                                                   │   (Native Mode) │
                                                   └─────────────────┘
```

### 3.2 Firestoreコレクション設計

```
knowledge (collection)
├── {document_id}
│   ├── id: string (ドキュメントID)
│   ├── title: string
│   ├── content: string
│   ├── user_id: string
│   ├── source: string ("personal" | "team")
│   ├── status: string ("draft" | "proposed" | "promoted")
│   ├── tags: array<string>
│   ├── schema_version: number (初期値: 1)
│   ├── created_at: timestamp
│   └── updated_at: timestamp
```

### 3.3 インデックス設計

以下の複合インデックスが必要になる可能性がある（自動作成されない場合）:

| フィールド1 | フィールド2 | 用途 |
|------------|------------|------|
| `status` | `created_at` (DESC) | ステータス別の最新順表示 |
| `user_id` | `created_at` (DESC) | ユーザー別の最新順表示 |
| `tags` (array_contains) | `created_at` (DESC) | タグ検索の最新順表示 |

---

## 4. リスクと対策

### Risk 1: プロキシプロセスの管理

**リスク**: `gcloud run services proxy`を常時起動しておく必要がある

**対策**:
- Claude Code起動前にプロキシを開始するワークフローを確立
- ターミナルの別タブでプロキシを常時起動
- 必要に応じてlaunchd/systemdでサービス化

### Risk 2: Firestoreのフルテキスト検索制限

**リスク**: 部分一致検索ができない

**対策**:
- Phase 2では前方一致検索とタグ検索で対応
- Phase 3でVertex AI Searchを導入し、セマンティック検索を実現

### Risk 3: 複数タグのAND検索

**リスク**: Firestoreは1クエリで複数の`array_contains`を使用できない

**対策**:
- 1つ目のタグでFirestoreクエリを実行
- 2つ目以降のタグはクライアントサイドでフィルタ
- または、タグの組み合わせを別フィールドに正規化して保存

---

## 5. 次のステップ

1. **PR #3b**: Cloud Run Invoker権限を設定し、未認証アクセスを無効化
2. **PR #3c**: Firestoreデータベースを作成し、モデル・リポジトリを実装
3. **PR #3d**: save_knowledge をFirestore保存に置き換え
4. **PR #3e**: search_knowledge をFirestore検索に置き換え

---

## 参考資料

- [Google Cloud Firestore Python Client](https://context7.com/googleapis/python-firestore)
- [Host MCP servers on Cloud Run](https://docs.cloud.google.com/run/docs/host-mcp-servers)
- [Authenticate developers | Cloud Run](https://docs.cloud.google.com/run/docs/authenticating/developers)
- [Connect Claude Code to tools via MCP](https://code.claude.com/docs/en/mcp)
