# Verification: ナレッジ昇格とアーカイブ機能の追加

このファイルは、promote_knowledge ツールと関連機能の受け入れテストをRunme.dev形式で記述します。

## 前提条件

- gcloud CLIインストール済み
- `gcloud auth application-default login` 完了
- Vector Search Collection作成済み（infra/README.md参照）
- archived_knowledge Collection作成済み（infra/README.md参照）
- Cloud Runデプロイ済み（--no-allow-unauthenticated）

---

## Setup

```sh {"background":"true","name":"pa-setup-proxy"}
# gcloud proxyをバックグラウンドで起動
gcloud run services proxy knowledge-mcp-server --region us-central1 --port=3000
```

```sh {"name":"pa-wait-proxy"}
# プロキシ起動を待機
sleep 5
export SERVICE_URL="http://localhost:3000"
echo "SERVICE_URL: $SERVICE_URL"
curl -s "$SERVICE_URL/health" | jq .
```

---

## Normal Path（正常系）

### Health Check

```sh {"name":"pa-test-health"}
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

### promote_knowledge: ナレッジ昇格成功

```sh {"name":"pa-test-promote-success"}
export SERVICE_URL="http://localhost:3000"
# まずテスト用ナレッジを保存（personal/draft状態）
SAVE_RESPONSE=$(curl -s -X POST "${SERVICE_URL}/mcp" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "save_knowledge",
      "arguments": {
        "title": "Promote Test Knowledge",
        "content": "This knowledge will be promoted to proposed status",
        "tags": ["test", "promote"]
      }
    }
  }')
echo "Save response: $SAVE_RESPONSE"

# IDを抽出
KNOWLEDGE_ID=$(echo "$SAVE_RESPONSE" | sed -n 's/.*"id":"\([^"]*\)".*/\1/p' | head -1)
echo "Knowledge ID: $KNOWLEDGE_ID"

# promote_knowledgeツールで昇格
PROMOTE_RESPONSE=$(curl -s -X POST "${SERVICE_URL}/mcp" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d "{
    \"jsonrpc\": \"2.0\",
    \"id\": 2,
    \"method\": \"tools/call\",
    \"params\": {
      \"name\": \"promote_knowledge\",
      \"arguments\": {
        \"id\": \"$KNOWLEDGE_ID\"
      }
    }
  }")
echo "Promote response: $PROMOTE_RESPONSE"

# 期待値:
# - status: "promoted" または "success"
# - id: ナレッジのID
# - current_status: "proposed"

# クリーンアップ
curl -s -X POST "${SERVICE_URL}/mcp" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d "{
    \"jsonrpc\": \"2.0\",
    \"id\": 3,
    \"method\": \"tools/call\",
    \"params\": {
      \"name\": \"delete_knowledge\",
      \"arguments\": {
        \"id\": \"$KNOWLEDGE_ID\"
      }
    }
  }" > /dev/null
echo "Test knowledge cleaned up"
```

### promote後の検索でstatus=proposed確認

```sh {"name":"pa-test-search-after-promote"}
export SERVICE_URL="http://localhost:3000"
# テスト用ナレッジを保存
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
        "title": "Search After Promote Test",
        "content": "Verify search returns proposed status after promotion",
        "tags": ["test", "search-promote"]
      }
    }
  }')
KNOWLEDGE_ID=$(echo "$SAVE_RESPONSE" | sed -n 's/.*"id":"\([^"]*\)".*/\1/p' | head -1)
echo "Saved knowledge ID: $KNOWLEDGE_ID"

# 昇格
curl -s -X POST "${SERVICE_URL}/mcp" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d "{
    \"jsonrpc\": \"2.0\",
    \"id\": 11,
    \"method\": \"tools/call\",
    \"params\": {
      \"name\": \"promote_knowledge\",
      \"arguments\": {
        \"id\": \"$KNOWLEDGE_ID\"
      }
    }
  }" > /dev/null

# 検索で status=proposed を確認
SEARCH_RESPONSE=$(curl -s -X POST "${SERVICE_URL}/mcp" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 12,
    "method": "tools/call",
    "params": {
      "name": "search_knowledge",
      "arguments": {
        "query": "Search After Promote Test",
        "limit": 5
      }
    }
  }')
echo "Search response: $SEARCH_RESPONSE"

# 期待値:
# - 検索結果にstatus: "proposed" が含まれる

# クリーンアップ
curl -s -X POST "${SERVICE_URL}/mcp" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d "{
    \"jsonrpc\": \"2.0\",
    \"id\": 13,
    \"method\": \"tools/call\",
    \"params\": {
      \"name\": \"delete_knowledge\",
      \"arguments\": {
        \"id\": \"$KNOWLEDGE_ID\"
      }
    }
  }" > /dev/null
```

---

## Edge Cases（異常系）

### promote_knowledge: 存在しないIDエラー

```sh {"name":"pa-test-promote-not-found"}
export SERVICE_URL="http://localhost:3000"
# 存在しないIDで昇格を試みる
RESPONSE=$(curl -s -X POST "${SERVICE_URL}/mcp" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 20,
    "method": "tools/call",
    "params": {
      "name": "promote_knowledge",
      "arguments": {
        "id": "non-existent-id-12345"
      }
    }
  }')

echo "$RESPONSE"

# 期待値:
# - エラーレスポンス
# - エラーメッセージに "knowledge not found" が含まれる
if echo "$RESPONSE" | grep -qi "knowledge not found"; then
  echo "PASS: Error message contains 'knowledge not found'"
elif echo "$RESPONSE" | grep -q "Unknown tool"; then
  echo "RED: Tool not implemented yet (expected during skeleton phase)"
else
  echo "FAIL: Unexpected response"
  exit 1
fi
```

### promote_knowledge: 既にproposed状態のナレッジ

```sh {"name":"pa-test-promote-already-proposed"}
export SERVICE_URL="http://localhost:3000"
# テスト用ナレッジを保存して昇格
SAVE_RESPONSE=$(curl -s -X POST "${SERVICE_URL}/mcp" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 30,
    "method": "tools/call",
    "params": {
      "name": "save_knowledge",
      "arguments": {
        "title": "Already Proposed Test",
        "content": "This will be promoted twice",
        "tags": ["test"]
      }
    }
  }')
KNOWLEDGE_ID=$(echo "$SAVE_RESPONSE" | sed -n 's/.*"id":"\([^"]*\)".*/\1/p' | head -1)
echo "Knowledge ID: $KNOWLEDGE_ID"

# 1回目の昇格
curl -s -X POST "${SERVICE_URL}/mcp" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d "{
    \"jsonrpc\": \"2.0\",
    \"id\": 31,
    \"method\": \"tools/call\",
    \"params\": {
      \"name\": \"promote_knowledge\",
      \"arguments\": {
        \"id\": \"$KNOWLEDGE_ID\"
      }
    }
  }" > /dev/null

# 2回目の昇格（エラーになるべき）
RESPONSE=$(curl -s -X POST "${SERVICE_URL}/mcp" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d "{
    \"jsonrpc\": \"2.0\",
    \"id\": 32,
    \"method\": \"tools/call\",
    \"params\": {
      \"name\": \"promote_knowledge\",
      \"arguments\": {
        \"id\": \"$KNOWLEDGE_ID\"
      }
    }
  }")

echo "$RESPONSE"

# 期待値:
# - エラーレスポンス
# - エラーメッセージに "only draft knowledge can be promoted" が含まれる
if echo "$RESPONSE" | grep -qi "only draft knowledge can be promoted"; then
  echo "PASS: Error message contains 'only draft knowledge can be promoted'"
elif echo "$RESPONSE" | grep -q "Unknown tool"; then
  echo "RED: Tool not implemented yet (expected during skeleton phase)"
else
  echo "FAIL: Unexpected response"
  exit 1
fi

# クリーンアップ
curl -s -X POST "${SERVICE_URL}/mcp" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d "{
    \"jsonrpc\": \"2.0\",
    \"id\": 33,
    \"method\": \"tools/call\",
    \"params\": {
      \"name\": \"delete_knowledge\",
      \"arguments\": {
        \"id\": \"$KNOWLEDGE_ID\"
      }
    }
  }" > /dev/null
```

### promote_knowledge: idが空の場合エラー

```sh {"name":"pa-test-promote-empty-id"}
export SERVICE_URL="http://localhost:3000"
# idが空の場合のエラーテスト
RESPONSE=$(curl -s -X POST "${SERVICE_URL}/mcp" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 40,
    "method": "tools/call",
    "params": {
      "name": "promote_knowledge",
      "arguments": {
        "id": ""
      }
    }
  }')

echo "$RESPONSE"

# 期待値:
# - エラーレスポンス
# - エラーメッセージに "id is required" が含まれる
if echo "$RESPONSE" | grep -qi "id is required"; then
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

### 保存→昇格→検索→削除の統合フロー

```sh {"name":"pa-test-save-promote-search-delete"}
export SERVICE_URL="http://localhost:3000"
echo "=== Integration Test: Save -> Promote -> Search -> Delete ==="

# 1. ナレッジを保存
echo "Step 1: Saving knowledge..."
SAVE_RESPONSE=$(curl -s -X POST "${SERVICE_URL}/mcp" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 50,
    "method": "tools/call",
    "params": {
      "name": "save_knowledge",
      "arguments": {
        "title": "Integration Promote Test",
        "content": "Full integration test for promote workflow",
        "tags": ["integration", "promote"]
      }
    }
  }')
echo "Save response: $SAVE_RESPONSE"

KNOWLEDGE_ID=$(echo "$SAVE_RESPONSE" | sed -n 's/.*"id":"\([^"]*\)".*/\1/p' | head -1)
echo "Knowledge ID: $KNOWLEDGE_ID"

# 2. ナレッジを昇格
echo "Step 2: Promoting knowledge..."
PROMOTE_RESPONSE=$(curl -s -X POST "${SERVICE_URL}/mcp" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d "{
    \"jsonrpc\": \"2.0\",
    \"id\": 51,
    \"method\": \"tools/call\",
    \"params\": {
      \"name\": \"promote_knowledge\",
      \"arguments\": {
        \"id\": \"$KNOWLEDGE_ID\"
      }
    }
  }")
echo "Promote response: $PROMOTE_RESPONSE"

# 3. 昇格したナレッジを検索
echo "Step 3: Searching for promoted knowledge..."
SEARCH_RESPONSE=$(curl -s -X POST "${SERVICE_URL}/mcp" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 52,
    "method": "tools/call",
    "params": {
      "name": "search_knowledge",
      "arguments": {
        "query": "integration promote workflow",
        "limit": 10
      }
    }
  }')
echo "Search response: $SEARCH_RESPONSE"

# 4. ナレッジを削除
echo "Step 4: Deleting test knowledge..."
DELETE_RESPONSE=$(curl -s -X POST "${SERVICE_URL}/mcp" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d "{
    \"jsonrpc\": \"2.0\",
    \"id\": 53,
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

```sh {"name":"pa-cleanup-test-data"}
export SERVICE_URL="http://localhost:3000"
# テストデータをクリーンアップ（検索して削除）
echo "Searching for test data..."
SEARCH_RESPONSE=$(curl -s -X POST "${SERVICE_URL}/mcp" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 90,
    "method": "tools/call",
    "params": {
      "name": "search_knowledge",
      "arguments": {
        "query": "Promote Test",
        "limit": 20
      }
    }
  }')
echo "Search response: $SEARCH_RESPONSE"

# IDを抽出して削除
IDS=$(echo "$SEARCH_RESPONSE" | grep -oE '"id":"[^"]*"' | sed 's/"id":"//g' | sed 's/"//g')
for ID in $IDS; do
  echo "Deleting: $ID"
  curl -s -X POST "${SERVICE_URL}/mcp" \
    -H "Content-Type: application/json" \
    -H "Accept: application/json, text/event-stream" \
    -d "{
      \"jsonrpc\": \"2.0\",
      \"id\": 91,
      \"method\": \"tools/call\",
      \"params\": {
        \"name\": \"delete_knowledge\",
        \"arguments\": {
          \"id\": \"$ID\"
        }
      }
    }"
  echo ""
done
echo "Cleanup complete"
```

```sh {"name":"pa-stop-proxy"}
# プロキシ停止（バックグラウンドで起動している場合）
pkill -f "gcloud run services proxy" || true
echo "Proxy stopped"
```

---

## Auto-Test Targets（自動テストでカバーすべき内容）

> このセクションは、ユニットテストでカバーすべきシナリオを明示します。
> Step 4（Logic Meat）で自動テストを追加する際の参照として使用してください。

### Primary Test Cases（主要ケース）

| Requirement | Scenario | WHEN/THEN | Priority | Reason |
|-------------|----------|-----------|----------|--------|
| Promote Knowledge | 正常昇格 | draft → proposed | P1 | 正常系コアパス |
| Promote Knowledge | 存在しないID | id指定 → エラー | P1 | エラーハンドリング |
| Promote Knowledge | 昇格不可状態 | proposed/promoted → エラー | P2 | 状態遷移バリデーション |
| Promote Knowledge | id空エラー | 空文字 → エラー | P2 | 入力バリデーション |
| Repository | update_status | id+status → 更新 | P1 | 状態更新ロジック |
| Repository | find_by_github_path | path → Knowledge/None | P2 | 検索機能 |
| Repository | find_by_pr_url | url → Knowledge/None | P2 | 検索機能 |
| Archive | save | Knowledge → ArchivedKnowledge | P1 | アーカイブ保存 |
| Model | ArchivedKnowledge初期化 | dataclass検証 | P2 | モデル検証 |

### Test Selection Constraints（選定制約）

Step 4でテストケースを追加する際は、以下の制約を適用して過剰生成を防止します。

- [ ] **C1網羅**: 分岐網羅を満たす最小限のケースを抽出
- [ ] **同値分割**: 冗長なテストケースを統合（例: `""`, `None`, `"   "` → 代表値1件）
- [ ] **優先順位**: P1正常系1件 + P2境界値2件以内に絞る
- [ ] **インターフェース集中**: 外部から見た振る舞いのみテスト（内部実装詳細は除外）

### Expected Test Files

- `tests/test_promote_knowledge.py` - promote_knowledgeツールのユニットテスト
- `tests/test_archive_repository.py` - ArchivedKnowledgeRepositoryのユニットテスト
- `tests/test_models.py` - ArchivedKnowledgeモデルのユニットテスト（既存ファイルに追加可）

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

```sh {"name":"cc-pa-setup-mcp"}
# MCPサーバーを登録（初回のみ）
# gcloud proxyが起動している状態で実行

# 既存の登録を削除（存在する場合）
claude mcp remove knowledge-mcp 2>/dev/null || true

# MCPサーバーを追加（HTTP transport + /mcp エンドポイント）
claude mcp add knowledge-mcp --transport http http://localhost:3000/mcp
echo "MCP server registered"
```

### ナレッジ昇格ワークフローの検証

```sh {"name":"cc-pa-test-promote-workflow"}
# 完全なワークフロー: 保存 → 昇格 → 確認 → 削除
claude -p "以下のワークフローを実行してください:

1. save_knowledge ツールで以下のナレッジを保存:
   - タイトル: 'Claude Code昇格テスト'
   - 内容: 'このナレッジはClaude Code経由で保存され、昇格されます。'
   - タグ: ['claude-code', 'promote-test']

2. 保存したナレッジのIDを使って promote_knowledge ツールで昇格

3. search_knowledge ツールで '昇格テスト' を検索し、ステータスが proposed になっていることを確認

4. delete_knowledge ツールでテストナレッジを削除

各ステップの結果を報告してください。" \
  --allowedTools "mcp__knowledge-mcp__save_knowledge,mcp__knowledge-mcp__promote_knowledge,mcp__knowledge-mcp__search_knowledge,mcp__knowledge-mcp__delete_knowledge"
```

### MCP Server Cleanup

```sh {"name":"cc-pa-cleanup-mcp"}
# テスト後のクリーンアップ（必要に応じて）
claude mcp remove knowledge-mcp
echo "MCP server removed"
```
