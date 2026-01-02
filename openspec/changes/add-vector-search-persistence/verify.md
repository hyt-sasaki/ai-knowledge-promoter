# Verification: Vector Search 2.0による個人ナレッジの永続化と検索

このファイルは、Phase 2で実装したナレッジ永続化・検索機能の受け入れテストをRunme.dev形式で記述します。

## 前提条件

- gcloud CLIインストール済み
- `gcloud auth application-default login` 完了
- Vector Search Collection作成済み（infra/README.md参照）
- Cloud Runデプロイ済み（--no-allow-unauthenticated）

---

## Setup

```sh {"background":"true","name":"vs-setup-proxy"}
# gcloud proxyをバックグラウンドで起動
gcloud run services proxy knowledge-mcp-server --region us-central1 --port=3000
```

```sh {"name":"vs-wait-proxy"}
# プロキシ起動を待機
sleep 5
export SERVICE_URL="http://localhost:3000"
echo "SERVICE_URL: $SERVICE_URL"
curl -s "$SERVICE_URL/health" | jq .
```

---

## Normal Path（正常系）

### Health Check

```sh {"name":"vs-test-health"}
export SERVICE_URL="http://localhost:3000"
# ヘルスチェックエンドポイントのテスト
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "${SERVICE_URL}/health")
echo "HTTP Status: $HTTP_CODE"
if [ "$HTTP_CODE" = "200" ]; then
  echo "PASS: Health check returned 200"
else
  echo "FAIL: Expected 200, got $HTTP_CODE"
  exit 1
fi
```

### save_knowledge: ナレッジ保存成功

```sh {"name":"vs-test-save-knowledge"}
export SERVICE_URL="http://localhost:3000"
# save_knowledgeツールのテスト（MCP経由）
RESPONSE=$(curl -s -X POST "${SERVICE_URL}/mcp" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "save_knowledge",
      "arguments": {
        "title": "Vector Search Test",
        "content": "This is a test for Vector Search 2.0 integration",
        "tags": ["test", "vector-search"]
      }
    }
  }')

echo "$RESPONSE"

# 期待値:
# - status: "saved"
# - id: 保存されたナレッジのID
# - title: "Vector Search Test"
```

### search_knowledge: ナレッジ検索成功

```sh {"name":"vs-test-search-knowledge"}
export SERVICE_URL="http://localhost:3000"
# search_knowledgeツールのテスト（MCP経由）
RESPONSE=$(curl -s -X POST "${SERVICE_URL}/mcp" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "search_knowledge",
      "arguments": {
        "query": "vector search test",
        "limit": 5
      }
    }
  }')

echo "$RESPONSE"

# 期待値:
# - 検索結果のリストが返される
# - 各結果にid, title, scoreが含まれる
```

### delete_knowledge: ナレッジ削除成功

```sh {"name":"vs-test-delete-knowledge"}
export SERVICE_URL="http://localhost:3000"
# delete_knowledgeツールのテスト（MCP経由）
# まずテスト用ナレッジを保存
SAVE_RESPONSE=$(curl -s -X POST "${SERVICE_URL}/mcp" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 10,
    "method": "tools/call",
    "params": {
      "name": "save_knowledge",
      "arguments": {
        "title": "Delete Test",
        "content": "This knowledge will be deleted",
        "tags": ["test", "delete"]
      }
    }
  }')
echo "Save response: $SAVE_RESPONSE"

# IDを抽出（スタブ実装の場合は "stub-id-..." 形式）
# 実装後は実際のIDを抽出する
KNOWLEDGE_ID=$(echo "$SAVE_RESPONSE" | sed -n 's/.*"id":"\([^"]*\)".*/\1/p' | head -1)
echo "Knowledge ID: $KNOWLEDGE_ID"

# 削除テスト
DELETE_RESPONSE=$(curl -s -X POST "${SERVICE_URL}/mcp" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d "{
    \"jsonrpc\": \"2.0\",
    \"id\": 11,
    \"method\": \"tools/call\",
    \"params\": {
      \"name\": \"delete_knowledge\",
      \"arguments\": {
        \"id\": \"$KNOWLEDGE_ID\"
      }
    }
  }")
echo "Delete response: $DELETE_RESPONSE"

# 期待値:
# - status: "deleted"
# - id: 削除されたナレッジのID
```

---

## Edge Cases（異常系）

### save_knowledge: contentが空の場合エラー

```sh {"name":"vs-test-save-empty-content"}
export SERVICE_URL="http://localhost:3000"
# contentが空の場合のエラーテスト
RESPONSE=$(curl -s -X POST "${SERVICE_URL}/mcp" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "save_knowledge",
      "arguments": {
        "title": "Empty Content Test",
        "content": "",
        "tags": ["test"]
      }
    }
  }')

echo "$RESPONSE"

# 期待値:
# - エラーレスポンス
# - エラーメッセージに "content is required" が含まれる
if echo "$RESPONSE" | grep -q "content is required"; then
  echo "PASS: Error message contains 'content is required'"
else
  echo "FAIL: Expected error message 'content is required'"
  exit 1
fi
```

### search_knowledge: queryが空の場合エラー

```sh {"name":"vs-test-search-empty-query"}
export SERVICE_URL="http://localhost:3000"
# queryが空の場合のエラーテスト
RESPONSE=$(curl -s -X POST "${SERVICE_URL}/mcp" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 4,
    "method": "tools/call",
    "params": {
      "name": "search_knowledge",
      "arguments": {
        "query": "",
        "limit": 5
      }
    }
  }')

echo "$RESPONSE"

# 期待値:
# - エラーレスポンス
# - エラーメッセージに "query is required" が含まれる
if echo "$RESPONSE" | grep -q "query is required"; then
  echo "PASS: Error message contains 'query is required'"
else
  echo "FAIL: Expected error message 'query is required'"
  exit 1
fi
```

### delete_knowledge: idが空の場合エラー

```sh {"name":"vs-test-delete-empty-id"}
export SERVICE_URL="http://localhost:3000"
# idが空の場合のエラーテスト
RESPONSE=$(curl -s -X POST "${SERVICE_URL}/mcp" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 5,
    "method": "tools/call",
    "params": {
      "name": "delete_knowledge",
      "arguments": {
        "id": ""
      }
    }
  }')

echo "$RESPONSE"

# 期待値:
# - エラーレスポンス
# - エラーメッセージに "id is required" が含まれる
# - ツール未実装時は "Unknown tool" が返る（RED状態では許容）
if echo "$RESPONSE" | grep -q "id is required"; then
  echo "PASS: Error message contains 'id is required'"
elif echo "$RESPONSE" | grep -q "Unknown tool"; then
  echo "RED: Tool not implemented yet (expected during skeleton phase)"
else
  echo "FAIL: Unexpected response"
  exit 1
fi
```

---

## Integration Test（統合テスト）

### 保存→検索→削除の統合フロー

```sh {"name":"vs-test-save-search-delete"}
export SERVICE_URL="http://localhost:3000"
echo "=== Integration Test: Save -> Search -> Delete ==="

# 1. ナレッジを保存
echo "Step 1: Saving knowledge..."
SAVE_RESPONSE=$(curl -s -X POST "${SERVICE_URL}/mcp" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 20,
    "method": "tools/call",
    "params": {
      "name": "save_knowledge",
      "arguments": {
        "title": "Integration Test Knowledge",
        "content": "This content should be found by semantic search and then deleted",
        "tags": ["integration", "test"]
      }
    }
  }')
echo "Save response: $SAVE_RESPONSE"

# IDを抽出（macOS互換）
KNOWLEDGE_ID=$(echo "$SAVE_RESPONSE" | sed -n 's/.*"id":"\([^"]*\)".*/\1/p' | head -1)
echo "Knowledge ID: $KNOWLEDGE_ID"

# 2. 保存したナレッジをセマンティック検索で取得
echo "Step 2: Searching for saved knowledge..."
SEARCH_RESPONSE=$(curl -s -X POST "${SERVICE_URL}/mcp" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 21,
    "method": "tools/call",
    "params": {
      "name": "search_knowledge",
      "arguments": {
        "query": "semantic search content",
        "limit": 10
      }
    }
  }')
echo "Search response: $SEARCH_RESPONSE"

# 3. ナレッジを削除（クリーンアップ）
echo "Step 3: Deleting test knowledge..."
DELETE_RESPONSE=$(curl -s -X POST "${SERVICE_URL}/mcp" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d "{
    \"jsonrpc\": \"2.0\",
    \"id\": 22,
    \"method\": \"tools/call\",
    \"params\": {
      \"name\": \"delete_knowledge\",
      \"arguments\": {
        \"id\": \"$KNOWLEDGE_ID\"
      }
    }
  }")
echo "Delete response: $DELETE_RESPONSE"

echo "=== Integration Test Complete ==="
```

---

## Cleanup

```sh {"name":"vs-stop-proxy"}
# プロキシ停止（バックグラウンドで起動している場合）
pkill -f "gcloud run services proxy" || true
echo "Proxy stopped"
```

---

## Auto-Test Targets（自動テストでカバーすべき内容）

> このセクションは、ユニットテストでカバーすべきシナリオを明示します。
> Step 4（Logic Meat）で自動テストを追加する際の参照として使用してください。

### Unit Test Candidates

| Requirement | Scenario | Test Type | Reason |
|-------------|----------|-----------|--------|
| Save Knowledge | 正常保存 | Unit Test | Repository.save()のモック検証 |
| Save Knowledge | content空エラー | Unit Test | バリデーションロジック |
| Save Knowledge | title未指定時の自動生成 | Unit Test | ビジネスロジック |
| Search Knowledge | 正常検索 | Unit Test | Repository.search()のモック検証 |
| Search Knowledge | query空エラー | Unit Test | バリデーションロジック |
| Delete Knowledge | 正常削除 | Unit Test | Repository.delete()のモック検証 |
| Delete Knowledge | id空エラー | Unit Test | バリデーションロジック |
| Delete Knowledge | 存在しないID | Unit Test | エラーハンドリング |
| Knowledge Model | dataclass初期化 | Unit Test | モデル検証 |

### Expected Test Files

- `tests/test_save_knowledge.py` - save_knowledgeツールのユニットテスト
- `tests/test_search_knowledge.py` - search_knowledgeツールのユニットテスト
- `tests/test_delete_knowledge.py` - delete_knowledgeツールのユニットテスト
- `tests/test_models.py` - ドメインモデルのユニットテスト
- `tests/test_vector_search_repository.py` - VectorSearchKnowledgeRepositoryの統合テスト

### Coverage Expectations

- **ビジネスロジック・純粋関数**: ユニットテストで80%以上カバー
- **verify.md**: End-to-Endフローのみ（外部依存・結合）
- **テストピラミッド**: ユニットテスト >> 統合テスト（verify.md）

---

## Claude Code 結合テスト

> このセクションは、Claude Code CLIからMCPツールを呼び出すE2Eテストです。
> 実際のAIワークフローでの統合を検証します。

### 前提条件（Claude Code結合テスト用）

- Claude Code CLIインストール済み（`claude --version` で確認）
- MCPサーバー設定済み（下記Setup参照）
- gcloud proxyが起動中（上記Setupセクション参照）

### MCP Server Setup

```sh {"name":"cc-setup-mcp"}
# MCPサーバーを登録（初回のみ）
# gcloud proxyが起動している状態で実行

# 既存の登録を削除（存在する場合）
claude mcp remove knowledge-mcp 2>/dev/null || true

# MCPサーバーを追加
claude mcp add knowledge-mcp --transport sse -- http://localhost:3000/sse
echo "MCP server registered"
```

### セマンティック検索の精度検証

このシナリオでは、2つの異なるナレッジを保存し、特定のクエリで片方だけが高スコアで返されることを検証します。

#### Step 1: 2つの異なるナレッジを保存

```sh {"name":"cc-test-save-two-knowledge"}
# 2つの異なるトピックのナレッジを保存
# 1つ目: Pythonの非同期処理について
# 2つ目: 料理のレシピについて

claude -p "以下の2つのナレッジを save_knowledge ツールで保存してください:

1つ目のナレッジ:
- タイトル: 'Pythonの非同期処理入門'
- 内容: 'Pythonのasyncioライブラリを使った非同期処理の実装方法を解説します。async/await構文を使うことで、I/O待ち時間を効率的に活用できます。コルーチン、タスク、イベントループの概念を理解することが重要です。'
- タグ: ['python', 'asyncio', 'programming']

2つ目のナレッジ:
- タイトル: 'おいしいパスタの作り方'
- 内容: '本格的なイタリアンパスタの作り方を紹介します。麺を茹でる際は塩分濃度が重要です。ソースは弱火でじっくり煮込むことで、深い味わいが生まれます。最後にパルメザンチーズを振りかけて完成です。'
- タグ: ['cooking', 'pasta', 'recipe']" \
  --allowedTools "mcp__knowledge-mcp__save_knowledge"
```

#### Step 2: プログラミング関連のクエリで検索

```sh {"name":"cc-test-search-programming"}
# プログラミング関連のクエリで検索
# 期待: Pythonの非同期処理のナレッジが高スコアで、パスタのレシピは低スコアまたは表示されない

claude -p "search_knowledge ツールを使って、'Pythonで並行処理を実装する方法を知りたい' というクエリで検索してください。検索結果のスコアを確認し、どのナレッジがより関連性が高いか説明してください。" \
  --allowedTools "mcp__knowledge-mcp__search_knowledge"
```

#### Step 3: 料理関連のクエリで検索

```sh {"name":"cc-test-search-cooking"}
# 料理関連のクエリで検索
# 期待: パスタのレシピが高スコアで、Pythonの非同期処理は低スコアまたは表示されない

claude -p "search_knowledge ツールを使って、'イタリア料理のレシピ' というクエリで検索してください。検索結果のスコアを確認し、どのナレッジがより関連性が高いか説明してください。" \
  --allowedTools "mcp__knowledge-mcp__search_knowledge"
```

#### Step 4: テストデータのクリーンアップ

```sh {"name":"cc-test-cleanup-knowledge"}
# テストで保存したナレッジを削除
claude -p "search_knowledge ツールで 'Pythonの非同期処理入門' と 'おいしいパスタの作り方' をそれぞれ検索し、見つかったナレッジを delete_knowledge ツールで削除してください。" \
  --allowedTools "mcp__knowledge-mcp__search_knowledge,mcp__knowledge-mcp__delete_knowledge"
```

### MCP Server Cleanup

```sh {"name":"cc-cleanup-mcp"}
# テスト後のクリーンアップ（必要に応じて）
claude mcp remove knowledge-mcp
echo "MCP server removed"
```
