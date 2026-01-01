# Verification: 知識共有MCPサーバー

このファイルは、知識共有MCPサーバーの受け入れテスト（統合テスト/E2Eテスト）をRunme.dev形式で記述します。

## 環境変数

```sh {"name":"setup-env"}
# Cloud RunサービスURLを取得
export SERVICE_URL=$(gcloud run services describe knowledge-mcp-server \
  --region asia-northeast1 \
  --format="value(status.url)" 2>/dev/null || echo "")

if [ -z "$SERVICE_URL" ]; then
  echo "Warning: Cloud Run service not deployed yet. Using localhost for local testing."
  export SERVICE_URL="http://localhost:8080"
fi

echo "SERVICE_URL: $SERVICE_URL"
```

---

## Normal Path（正常系）

### Health Check

```sh {"name":"test-health"}
# ヘルスチェックエンドポイントのテスト
curl -s -o /dev/null -w "%{http_code}" "${SERVICE_URL}/health"

# 期待値:
# ステータスコード: 200
# レスポンス: OK
```

```sh {"name":"test-health-body"}
# ヘルスチェックのレスポンスボディ確認
curl -s "${SERVICE_URL}/health"

# 期待値: OK
```

### MCP Tools

> **Note**: PR #2b（MCPスケルトン）で実装予定。実装後に`excludeFromRunAll`を解除してください。

```sh {"excludeFromRunAll":"true","name":"test-save-knowledge"}
# save_knowledgeツールのテスト
curl -s -X POST "${SERVICE_URL}/mcp" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "save_knowledge",
      "arguments": {
        "title": "Test Knowledge",
        "content": "This is a test content",
        "tags": ["test", "sample"]
      }
    }
  }'

# 期待値:
# ステータスコード: 200
# レスポンス: {"jsonrpc": "2.0", "id": 1, "result": {"status": "saved", "id": "...", "title": "Test Knowledge"}}
```

```sh {"excludeFromRunAll":"true","name":"test-search-knowledge"}
# search_knowledgeツールのテスト
curl -s -X POST "${SERVICE_URL}/mcp" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "search_knowledge",
      "arguments": {
        "query": "test",
        "limit": 5
      }
    }
  }'

# 期待値:
# ステータスコード: 200
# レスポンス: {"jsonrpc": "2.0", "id": 2, "result": [{"id": "...", "title": "...", "score": ...}]}
```

---

## Edge Cases（異常系）

```sh {"excludeFromRunAll":"true","name":"test-invalid-tool"}
# 存在しないツール呼び出しテスト
curl -s -X POST "${SERVICE_URL}/mcp" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "invalid_tool",
      "arguments": {}
    }
  }'

# 期待値:
# ステータスコード: 200
# レスポンス: {"jsonrpc": "2.0", "id": 3, "error": {"code": -32601, "message": "Method not found"}}
```

