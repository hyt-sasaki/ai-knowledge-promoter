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

```sh {"name":"test-save-knowledge"}
# save_knowledgeツールのテスト
curl -s -X POST "${SERVICE_URL}/mcp" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
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
# レスポンス: event: message
# data: {"jsonrpc": "2.0", "id": 1, "result": {..., "structuredContent": {"status": "saved", "id": "...", "title": "Test Knowledge"}}}
```

```sh {"name":"test-search-knowledge"}
# search_knowledgeツールのテスト
curl -s -X POST "${SERVICE_URL}/mcp" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
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
# レスポンス: event: message
# data: {"jsonrpc": "2.0", "id": 2, "result": {..., "structuredContent": {"result": [{"id": "...", "title": "...", "score": ...}]}}}
```

---

## Edge Cases（異常系）

```sh {"excludeFromRunAll":"true","name":"test-invalid-tool"}
# 存在しないツール呼び出しテスト
curl -s -X POST "${SERVICE_URL}/mcp" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
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
# レスポンス: event: message
# data: {"jsonrpc": "2.0", "id": 3, "error": {"code": -32601, "message": "..."}}
```

---

## Claude Code 結合テスト

このセクションでは、Claude CodeからMCPサーバーへの結合テスト手順を記述します。

### 前提条件

MCPサーバーがuserスコープに登録されていること：

```sh {"name":"setup-mcp-server"}
# MCPサーバーをuserスコープに追加（未登録の場合）
claude mcp add --transport http knowledge-mcp https://knowledge-mcp-server-lqb45vmcbq-an.a.run.app/mcp --scope user 2>/dev/null || echo "Already registered or registration attempted"

# 登録状況を確認
claude mcp list | grep -E "(knowledge-mcp|Connected)"
```

### save_knowledge ツール呼び出し

```sh {"name":"test-claude-save-knowledge"}
# Claude Codeからsave_knowledgeツールを呼び出し
claude -p "save_knowledge ツールを使って、title='テスト知識', content='これはClaude Codeからの結合テストです', tags=['test', 'integration'] でナレッジを保存してください。ツール呼び出しの結果をそのまま表示してください。" --allowedTools "mcp__knowledge-mcp__save_knowledge"

# 期待値:
# レスポンスに以下が含まれる:
# - "status": "saved"
# - "id": "stub-id-..."
# - "title": "テスト知識"
```

### search_knowledge ツール呼び出し

```sh {"name":"test-claude-search-knowledge"}
# Claude Codeからsearch_knowledgeツールを呼び出し
claude -p "search_knowledge ツールを使って、query='テスト', limit=5 でナレッジを検索してください。ツール呼び出しの結果をそのまま表示してください。" --allowedTools "mcp__knowledge-mcp__search_knowledge"

# 期待値:
# レスポンスに以下が含まれる:
# - "id": "stub-1"
# - "title": "Sample: テスト"
# - "score": 0.95
```
