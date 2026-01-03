# Infrastructure Setup

このドキュメントは、GCPプロジェクトのセットアップ手順を記録しています。
Runme.dev形式で記述されており、各コマンドブロックを直接実行できます。

## 設定情報

| 項目 | 値 |
|------|-----|
| GCPプロジェクト名 | `ai-knowledge-promoter` |
| リージョン | `asia-northeast1`（東京） |
| Cloud Runサービス名 | `knowledge-mcp-server` |

## 前提条件

- gcloud CLI インストール済み
- Google Cloud アカウント
- 課金が有効なBillingアカウント

## 1. gcloud CLI認証

```sh {"name":"auth-login"}
gcloud auth login
```

## 2. GCPプロジェクト作成

```sh {"name":"create-project"}
gcloud projects create ai-knowledge-promoter --name="AI Knowledge Promoter"
```

```sh {"name":"set-project"}
gcloud config set project ai-knowledge-promoter
```

## 3. 課金アカウント紐付け

```sh {"name":"list-billing"}
# 課金アカウントIDを取得
gcloud billing accounts list
```

```sh {"name":"link-billing"}
# 課金アカウントを紐付け（BILLING_ACCOUNT_IDを実際の値に置換）
# 例: gcloud billing projects link ai-knowledge-promoter --billing-account=012345-6789AB-CDEF01
gcloud billing projects link ai-knowledge-promoter --billing-account=BILLING_ACCOUNT_ID
```

## 4. 必要なAPIの有効化

```sh {"name":"enable-apis"}
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable artifactregistry.googleapis.com
```

## 5. Cloud Runデプロイ

```sh {"cwd":"../mcp-server","name":"deploy-cloud-run"}
gcloud run deploy knowledge-mcp-server \
  --source . \
  --region asia-northeast1 \
  --allow-unauthenticated
```

## 6. デプロイ確認

```sh {"name":"describe-service"}
gcloud run services describe knowledge-mcp-server \
  --region asia-northeast1 \
  --format="value(status.url)"
```

## 7. ヘルスチェック

```sh {"name":"test-health"}
SERVICE_URL=$(gcloud run services describe knowledge-mcp-server \
  --region asia-northeast1 \
  --format="value(status.url)")
curl -s "${SERVICE_URL}/health"
```

## トラブルシューティング

### プロジェクトが既に存在する場合

```sh {"excludeFromRunAll":"true","name":"set-existing-project"}
gcloud config set project ai-knowledge-promoter
```

### APIが有効化されているか確認

```sh {"excludeFromRunAll":"true","name":"list-enabled-services"}
gcloud services list --enabled --filter="name:(run.googleapis.com OR cloudbuild.googleapis.com OR artifactregistry.googleapis.com)"
```

### Cloud Runサービスの削除（必要な場合）

```sh {"excludeFromRunAll":"true","name":"delete-service"}
gcloud run services delete knowledge-mcp-server --region asia-northeast1
```

---

# Phase 2: Vector Search 2.0 セットアップ

Phase 2ではナレッジの永続化とセマンティック検索を実装します。
Vertex AI Vector Search 2.0を使用し、Cloud Run Invoker認証でセキュアなアクセスを実現します。

## Phase 2 設定情報

| 項目 | 値 |
|------|-----|
| Vector Search リージョン | `us-central1` |
| Collection名 | `knowledge` |
| 認証方式 | Cloud Run Invoker + gcloud proxy |

## Phase 2.1 Vector Search API有効化

```sh {"name":"enable-vector-search-apis"}
gcloud services enable vectorsearch.googleapis.com aiplatform.googleapis.com \
    --project "ai-knowledge-promoter"
```

## Phase 2.2 Cloud Run IAM設定

Vector SearchにアクセスするためのIAM権限を付与します。

```sh {"name":"setup-iam"}
PROJECT_ID=$(gcloud config get-value project)
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/aiplatform.user"
```

## Phase 2.3 Collection作成

Collection作成スクリプトを実行します（初回1回のみ）。

```sh {"cwd":"../mcp-server","name":"create-collection"}
GCP_PROJECT_ID=ai-knowledge-promoter uv run python scripts/create_collection.py
```

## Phase 2.4 Cloud Run認証設定変更

認証を必須に変更します（`--no-allow-unauthenticated`）。

```sh {"cwd":"../mcp-server","name":"deploy-cloud-run-authenticated"}
gcloud run deploy knowledge-mcp-server \
  --source . \
  --region us-central1 \
  --no-allow-unauthenticated \
  --quiet
```

## Phase 2.5 gcloud proxy接続

ローカルからCloud Runに接続するためのプロキシを起動します。

```sh {"background":"true","name":"start-proxy"}
gcloud run services proxy knowledge-mcp-server --region us-central1 --port=3000
```

## Phase 2.6 プロキシ経由でヘルスチェック

```sh {"name":"test-health-via-proxy"}
curl -s "http://localhost:3000/health"
```

## Phase 2 トラブルシューティング

### Vector Search APIが有効か確認

```sh {"excludeFromRunAll":"true","name":"check-vector-search-api"}
gcloud services list --enabled --filter="name:(vectorsearch.googleapis.com OR aiplatform.googleapis.com)"
```

### IAM設定を確認

```sh {"excludeFromRunAll":"true","name":"check-iam"}
PROJECT_ID=$(gcloud config get-value project)
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")

gcloud projects get-iam-policy $PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --format="table(bindings.role)"
```

### Collectionの状態を確認

```sh {"cwd":"../mcp-server","excludeFromRunAll":"true","name":"check-collection"}
GCP_PROJECT_ID=ai-knowledge-promoter uv run python -c "
import os
from google.cloud import vectorsearch_v1beta
project_id = os.environ['GCP_PROJECT_ID']
location = os.environ.get('GCP_LOCATION', 'us-central1')
client = vectorsearch_v1beta.VectorSearchServiceClient()
collections = client.list_collections(parent=f'projects/{project_id}/locations/{location}')
for c in collections:
    print(f'{c.name}: {c.state}')
"
```

### Collection再作成（スキーマ変更時）

Vector Search 2.0は厳格なスキーマバリデーションを適用するため、スキーマ変更時はCollectionを再作成する必要があります。

> **注意**: この操作は既存のデータをすべて削除します。本番環境では事前にデータのバックアップを検討してください。

```sh {"cwd":"../mcp-server","excludeFromRunAll":"true","name":"delete-collection"}
# 既存のCollectionを削除（データも含めて削除）
GCP_PROJECT_ID=ai-knowledge-promoter uv run python scripts/delete_collection.py
```

```sh {"cwd":"../mcp-server","excludeFromRunAll":"true","name":"recreate-collection"}
# 新しいスキーマでCollectionを再作成
GCP_PROJECT_ID=ai-knowledge-promoter uv run python scripts/create_collection.py
```

---

# Phase 3: アーカイブ機能セットアップ

Phase 3では昇格完了時に元ナレッジをアーカイブする機能を実装します。
アーカイブ用の専用Collection `archived-knowledge` を使用します。

## Phase 3 設定情報

| 項目 | 値 |
|------|-----|
| Collection名 | `archived-knowledge` |
| リージョン | `us-central1`（knowledgeと同一） |
| 用途 | 昇格済み元ナレッジの保管（監査・追跡用） |

## Phase 3.1 Archived Knowledge Collection作成

アーカイブ用のCollection作成スクリプトを実行します（初回1回のみ）。

```sh {"cwd":"../mcp-server","name":"create-archived-collection"}
GCP_PROJECT_ID=ai-knowledge-promoter uv run python scripts/create_archived_collection.py
```

## Phase 3 トラブルシューティング

### Archived Collectionの状態を確認

```sh {"cwd":"../mcp-server","excludeFromRunAll":"true","name":"check-archived-collection"}
GCP_PROJECT_ID=ai-knowledge-promoter uv run python -c "
import os
from google.cloud import vectorsearch_v1beta
project_id = os.environ['GCP_PROJECT_ID']
location = os.environ.get('GCP_LOCATION', 'us-central1')
client = vectorsearch_v1beta.VectorSearchServiceClient()
collections = client.list_collections(parent=f'projects/{project_id}/locations/{location}')
for c in collections:
    if 'archived' in c.name:
        print(f'{c.name}')
"
```

### Archived Collection再作成

```sh {"cwd":"../mcp-server","excludeFromRunAll":"true","name":"delete-archived-collection"}
# 既存のCollectionを削除
GCP_PROJECT_ID=ai-knowledge-promoter COLLECTION_ID=archived-knowledge uv run python scripts/delete_collection.py
```

```sh {"cwd":"../mcp-server","excludeFromRunAll":"true","name":"recreate-archived-collection"}
# 再作成
GCP_PROJECT_ID=ai-knowledge-promoter uv run python scripts/create_archived_collection.py
```
