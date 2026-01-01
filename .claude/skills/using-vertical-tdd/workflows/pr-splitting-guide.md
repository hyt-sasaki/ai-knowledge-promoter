# PR分割ガイドライン

## 概要

実装フェーズにおけるPR分割の柔軟な戦略を定義します。提案フェーズは厳密に管理しつつ、実装フェーズは状況に応じてPRを分割し、レビュー負荷を軽減します。

## 基本原則

### PR分割の目安

- **変更ファイル数**: 10ファイル以下を目安
- **意味のある単位**: レイヤー単位、機能単位、デプロイ単位など
- **レビュー可能性**: 1PRで30分以内にレビューできる規模

### フェーズごとの方針

| フェーズ | PR管理 | 分割の自由度 |
|---------|--------|--------------|
| 提案フェーズ（Step 1, 1a, 1b） | 厳密に管理 | PR #1, #1.5で固定 |
| 実装フェーズ（Step 2-4） | 柔軟に分割 | 状況に応じて複数PR可 |
| リリースフェーズ（Step 5） | 厳密に管理 | PR #N（最終）で固定 |

## バリエーションパターン

### パターンA: アプリケーション型（従来通り）

既存システムへの機能追加、インフラ変更が少ない場合：

```
PR #1: 提案
  ↓
[PR #1a: Tech Spike（任意）]
  ↓
[PR #1b: 設計（任意）]
  ↓
PR #2: スケルトン（verify.md GREEN）
  ↓
PR #3: ロジック
  ↓
PR #N: リリース
```

### パターンB: インフラ先行型

新規インフラ構築、デプロイ基盤整備が必要な場合：

```
PR #1: 提案
  ↓
[PR #1a: Tech Spike（任意）]
  ↓
[PR #1b: 設計（任意）]
  ↓
PR #2a: デプロイ基盤（最小構成でデプロイ成功）
  ↓
PR #2b: スケルトン（verify.md GREEN）
  ↓
PR #3, #3a, #3b...: ロジック（必要に応じて分割）
  ↓
PR #N: リリース
```

### パターンB拡張: 細分化

デプロイ基盤PRが大きくなる場合、さらに細分化：

```
PR #2a: GCPプロジェクト設定・IAM
  ↓
PR #2b: HTTPサーバー最小構成（/health のみ）
  ↓
PR #2c: Cloud Runデプロイ成功確認
  ↓
PR #2d: MCP機能追加（スケルトン）
  ↓
...
```

## 中間PR（部分実装）のテスト戦略

verify.mdがまだ完全にGREENでない状態でPRをマージする場合の戦略です。

### pytest等のテストフレームワーク

`@pytest.mark.skip` を使用：

```python
import pytest

@pytest.mark.skip(reason="Implemented in PR #2b: MCP skeleton")
def test_save_knowledge():
    """save_knowledge ツールのテスト"""
    pass

@pytest.mark.skip(reason="Implemented in PR #2b: MCP skeleton")
def test_search_knowledge():
    """search_knowledge ツールのテスト"""
    pass

# このPRで実装済みのテストは通常通り実行
def test_health_endpoint():
    """/health エンドポイントのテスト"""
    response = client.get("/health")
    assert response.status_code == 200
```

### runme.dev (verify.md)

コメントアウト + 理由コメントを使用：

```markdown
## Normal Path（正常系）

```sh {"name":"test-health"}
# /health エンドポイントテスト - このPRで実装済み
curl -X GET http://localhost:8080/health
# 期待: {"status": "ok"}
```

## Pending Tests（後続PRで実装予定）

以下のテストは後続のPRで実装されます。

<!-- [PENDING] PR #2b: MCP skeleton で実装予定
```sh {"name":"test-save-knowledge"}
curl -X POST http://localhost:8080/mcp/tools/save_knowledge \
  -H "Content-Type: application/json" \
  -d '{"content": "test knowledge"}'
# 期待: {"id": "..."}
```
-->

<!-- [PENDING] PR #2b: MCP skeleton で実装予定
```sh {"name":"test-search-knowledge"}
curl -X POST http://localhost:8080/mcp/tools/search_knowledge \
  -H "Content-Type: application/json" \
  -d '{"query": "test"}'
# 期待: {"results": [...]}
```
-->
```

### verify-all の更新

中間PRでは、実装済みのテストのみを `verify-all` に含めます：

```markdown
```sh {"name":"verify-all"}
# このPRで実装済みのテストのみ実行
runme run setup
runme run test-health
runme run cleanup
echo "✅ All implemented tests passed"
echo "⏳ Pending: test-save-knowledge, test-search-knowledge (PR #2b)"
```
```

### tasks.mdにスキップ解除タスクを追記

テストをスキップした場合、**必ず**tasks.mdにスキップ解除タスクを追記して忘れを防ぎます：

```markdown
### PR #2b: MCPスケルトン
- [ ] test-save-knowledge スキップ解除
- [ ] test-search-knowledge スキップ解除
- [ ] MCPサーバー実装
- [ ] verify.md全テストGREEN確認
```

**重要**: スキップしたテストごとに解除タスクを作成し、後続PRで確実に解除します。

## PR説明テンプレート

### 中間PR（部分実装）の場合

```markdown
## [Infrastructure] Cloud Run デプロイ基盤

This PR sets up the deployment infrastructure for the MCP server.

### What's Included

- ✅ GCPプロジェクト設定
- ✅ Cloud Run サービスアカウント・IAM
- ✅ 最小HTTPサーバー（/health エンドポイント）
- ✅ Buildpacks でのデプロイ成功確認

### What's NOT Included (Pending)

- ⏳ save_knowledge ツール → PR #2b
- ⏳ search_knowledge ツール → PR #2b
- ⏳ MCP プロトコル対応 → PR #2b

### Test Status

| テスト | ステータス | 備考 |
|--------|-----------|------|
| test-health | ✅ GREEN | このPRで実装 |
| test-save-knowledge | ⏳ SKIP | PR #2bで実装予定 |
| test-search-knowledge | ⏳ SKIP | PR #2bで実装予定 |

### Verification

```bash
runme run verify-all
# ✅ test-health passed
# ⏳ Pending: test-save-knowledge, test-search-knowledge
```

### Next Steps

- [ ] このPR: デプロイ基盤
- [ ] PR #2b: MCPスケルトン
- [ ] PR #3: ロジック実装
- [ ] PR #N: リリース
```

## 分割判断のフローチャート

```
変更ファイル数 > 10?
  ├─ Yes → 分割を検討
  │   ├─ インフラ/デプロイ変更あり?
  │   │   ├─ Yes → パターンB（インフラ先行型）を採用
  │   │   └─ No → 機能単位で分割
  │   └─ レイヤー単位で分割可能?
  │       ├─ Yes → レイヤーごとにPR作成
  │       └─ No → 最も自然な境界で分割
  └─ No → 1PRでOK
```

## 具体例: add-knowledge-mcp-skeleton

### 元の計画（1PR）

```markdown
## 2. 実装フェーズ
- [ ] verify.md作成
- [ ] REDステータス確認
- [ ] GCPプロジェクト基盤整備
- [ ] Cloud Run + Buildpacks デプロイ検証
- [ ] MCPサーバー実装
- [ ] Cloud Runへ再デプロイ・疎通確認
- [ ] スケルトン実装完了（GREEN確認）
- [ ] PR #2作成・マージ
```

### 分割後の計画（3PR）

```markdown
## 2. 実装フェーズ

### PR #2a: デプロイ基盤
- [ ] GCPプロジェクト基盤整備
  - [ ] Cloud Run サービスアカウント設定
  - [ ] IAMポリシー設定
- [ ] Cloud Run + Buildpacks デプロイ検証（MCPなし最小構成）
  - [ ] uvベースプロジェクト作成
  - [ ] 最小限のHTTPサーバー（/health のみ）
  - [ ] `gcloud run deploy --source .` でデプロイ成功確認

### PR #2b: MCPスケルトン
- [ ] verify.md作成（Runme.dev形式）
- [ ] REDステータス確認
- [ ] MCPサーバー実装
  - [ ] FastMCP プロジェクト構成
  - [ ] save_knowledge ツール（スタブ）
  - [ ] search_knowledge ツール（スタブ）
- [ ] Cloud Runへ再デプロイ・疎通確認
- [ ] スケルトン実装完了（GREEN確認）

### PR #3: ロジック実装
- [ ] Firestore連携実装
- [ ] Vertex AI Search統合
- [ ] ユニットテスト実装
```

## よくある質問

**Q: 提案フェーズでもPRを分割できますか？**

A: 原則として提案フェーズは PR #1（proposal.md + tasks.md）、PR #1a（Tech Spike、任意）、PR #1b（設計、任意）に固定します。提案の粒度を小さくしたい場合は、OpenSpec提案自体を分割することを検討してください。

**Q: 中間PRでverify.mdがREDのままマージして問題ないですか？**

A: 問題ありません。ただし以下を必ず守ってください：
- スキップ理由を明記する
- PR説明で何が未実装か明確にする
- 後続PRで必ず実装する

**Q: PR分割の目安「10ファイル」は厳密なルールですか？**

A: 厳密なルールではなく目安です。意味のある単位で分割することが優先です。例えば、関連する15ファイルを無理に分割するより、まとまった機能として1PRにする方が適切な場合もあります。

**Q: インフラ先行型を選ぶ基準は？**

A: 以下のいずれかに該当する場合：
- 新規GCP/AWS/Azureリソースの作成が必要
- 新しいデプロイパイプラインの構築が必要
- 既存インフラへの大幅な変更が必要
- デプロイ成功確認が不確実な要素がある

## 参考リソース

- [コミット戦略](commit-strategy.md)
- [Step 3: Skeleton Green](step3-skeleton-green.md)
- [Step 4: Logic Meat](step4-logic-meat.md)
