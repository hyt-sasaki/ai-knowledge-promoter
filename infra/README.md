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
