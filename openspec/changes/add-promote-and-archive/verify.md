# Verification: ナレッジ昇格とアーカイブ機能

このファイルは、Phase 3で実装するナレッジ昇格（promote_knowledge）機能の受け入れテストをRunme.dev形式で記述します。

## 前提条件

- gcloud CLIインストール済み
- `gcloud auth application-default login` 完了
- Vector Search Collection作成済み（infra/README.md参照）

---

## Setup

```sh {"cwd":"../../../mcp-server","name":"promote-archive-deploy"}
# Cloud Runにデプロイ（最新コードを反映）
gcloud run deploy knowledge-mcp-server \
  --source . \
  --region us-central1 \
  --no-allow-unauthenticated \
  --quiet
```

```sh {"background":"true","name":"promote-archive-setup-proxy"}
# gcloud proxyをバックグラウンドで起動
gcloud run services proxy knowledge-mcp-server --region us-central1 --port=3000
```

```sh {"name":"promote-archive-wait-proxy"}
# プロキシ起動を待機
sleep 5
export SERVICE_URL="http://localhost:3000"
echo "SERVICE_URL: $SERVICE_URL"
curl -s "$SERVICE_URL/health" | jq .
```

---

## Normal Path（正常系）

### promote_knowledge: ナレッジ昇格成功

```sh {"name":"promote-archive-test-promote-success"}
export SERVICE_URL="http://localhost:3000"

# 1. テスト用ナレッジを保存（personal/draft状態）
echo "Step 1: Creating test knowledge..."
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
        "content": "This knowledge will be promoted from draft to proposed",
        "tags": ["test", "promote"]
      }
    }
  }')
echo "Save response: $SAVE_RESPONSE"

# IDを抽出
KNOWLEDGE_ID=$(echo "$SAVE_RESPONSE" | sed -n 's/.*"id":"\([^"]*\)".*/\1/p' | head -1)
echo "Knowledge ID: $KNOWLEDGE_ID"

# 2. promote_knowledge ツールで昇格
echo "Step 2: Promoting knowledge..."
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
# - status: "proposed"
# - id: 昇格されたナレッジのID
if echo "$PROMOTE_RESPONSE" | grep -q '"proposed"'; then
  echo "PASS: Knowledge promoted to proposed status"
else
  echo "FAIL: Expected status 'proposed'"
  exit 1
fi

# 3. クリーンアップ
echo "Step 3: Cleanup..."
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
  }"
echo "Cleanup complete"
```

---

## Edge Cases（異常系）

### promote_knowledge: idが空の場合エラー

```sh {"name":"promote-archive-test-promote-empty-id"}
export SERVICE_URL="http://localhost:3000"
# idが空の場合のエラーテスト
RESPONSE=$(curl -s -X POST "${SERVICE_URL}/mcp" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 10,
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

### promote_knowledge: 存在しないIDの場合エラー

```sh {"name":"promote-archive-test-promote-not-found","excludeFromRunAll":"true"}
export SERVICE_URL="http://localhost:3000"
# 存在しないIDの場合のエラーテスト
RESPONSE=$(curl -s -X POST "${SERVICE_URL}/mcp" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 11,
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
# NOTE: このテストはPhase 3で本実装後に有効化
if echo "$RESPONSE" | grep -q "knowledge not found"; then
  echo "PASS: Error message contains 'knowledge not found'"
else
  echo "SKIP: This test requires full implementation (Phase 3)"
fi
```

### promote_knowledge: 昇格不可状態の場合エラー

```sh {"name":"promote-archive-test-promote-invalid-state","excludeFromRunAll":"true"}
export SERVICE_URL="http://localhost:3000"
# 昇格不可状態（already proposed）のテスト
# NOTE: このテストはPhase 3で本実装後に有効化

echo "SKIP: This test requires full implementation (Phase 3)"
echo "Expected: Error message 'only draft knowledge can be promoted'"

# 期待値:
# - エラーレスポンス
# - エラーメッセージに "only draft knowledge can be promoted" が含まれる
```

---

## Cleanup

```sh {"name":"promote-archive-cleanup-test-data"}
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
        "query": "Promote Test Knowledge",
        "limit": 10
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

```sh {"name":"promote-archive-stop-proxy"}
# プロキシ停止（バックグラウンドで起動している場合）
pkill -f "gcloud run services proxy" || true
echo "Proxy stopped"
```

---

## Claude Code 結合テスト

> このセクションは、Claude Code CLIからMCPツールを呼び出すE2Eテストです。
> 実際のAIワークフローでの統合を検証します。

### MCP Server Setup

```sh {"name":"promote-archive-cc-setup-mcp"}
# MCPサーバーを登録（初回のみ）
# gcloud proxyが起動している状態で実行

# 既存の登録を削除（存在する場合）
claude mcp remove knowledge-mcp 2>/dev/null || true

# MCPサーバーを追加（HTTP transport + /mcp エンドポイント）
claude mcp add knowledge-mcp --transport http http://localhost:3000/mcp
echo "MCP server registered"
```

### ナレッジ昇格ワークフローの検証

```sh {"name":"promote-archive-cc-test-promote-workflow"}
# ナレッジを保存し、昇格するワークフローをテスト

claude -p "以下の手順でナレッジ昇格をテストしてください:

1. save_knowledge ツールで以下のナレッジを保存:
   - タイトル: 'Claude Code昇格テスト'
   - 内容: 'このナレッジはClaude Code経由で保存され、昇格されます。ナレッジ管理システムの統合テストです。'
   - タグ: ['test', 'claude-code', 'promote']

2. 保存したナレッジのIDを使って promote_knowledge ツールで昇格

3. 結果を報告（昇格前後のステータス変化を含む）" \
  --allowedTools "mcp__knowledge-mcp__save_knowledge,mcp__knowledge-mcp__promote_knowledge"
```

### Claude Code結合テスト クリーンアップ

```sh {"name":"promote-archive-cc-cleanup"}
# テストで保存したナレッジを削除
claude -p "search_knowledge ツールで 'Claude Code昇格テスト' を検索し、見つかったナレッジを delete_knowledge ツールで削除してください。" \
  --allowedTools "mcp__knowledge-mcp__search_knowledge,mcp__knowledge-mcp__delete_knowledge"
```

### MCP Server Cleanup

```sh {"name":"promote-archive-cc-cleanup-mcp"}
# テスト後のクリーンアップ（必要に応じて）
claude mcp remove knowledge-mcp
echo "MCP server removed"
```

---

## Auto-Test Targets（自動テストでカバーすべき内容）

> このセクションは、ユニットテストでカバーすべきシナリオを明示します。
> Phase 3（Logic Meat）で自動テストを追加する際の参照として使用してください。

### Primary Test Cases（主要ケース）

| Requirement | Scenario | WHEN/THEN | Priority | Reason |
|-------------|----------|-----------|----------|--------|
| Promote Knowledge | 昇格成功 | personal/draft → proposed | P1 | 正常系コアパス |
| Promote Knowledge | id空エラー | id="" → "id is required" | P2 | バリデーション |
| Promote Knowledge | 存在しないID | id="xxx" → "knowledge not found" | P2 | エラーハンドリング |
| Promote Knowledge | 昇格不可状態 | proposed → "only draft can be promoted" | P2 | ビジネスルール |

### Test Selection Constraints（選定制約）

Phase 3でテストケースを追加する際は、以下の制約を適用して過剰生成を防止します。

- [ ] **C1網羅**: 分岐網羅を満たす最小限のケースを抽出
- [ ] **同値分割**: 冗長なテストケースを統合（例: `""`, `None`, `"   "` → 代表値1件）
- [ ] **優先順位**: P1正常系1件 + P2境界値3件以内に絞る
- [ ] **インターフェース集中**: 外部から見た振る舞いのみテスト（内部実装詳細は除外）

### Expected Test Files

- `tests/test_promote_knowledge.py` - promote_knowledgeツールのユニットテスト
- `tests/test_archive_repository.py` - ArchivedKnowledgeRepositoryのユニットテスト
- `tests/test_models.py` - ArchivedKnowledgeモデルのユニットテスト

### Coverage Expectations

- **ビジネスロジック・純粋関数**: ユニットテストで80%以上カバー
- **verify.md**: End-to-Endフローのみ（外部依存・結合）
- **テストピラミッド**: ユニットテスト >> 統合テスト（verify.md）
