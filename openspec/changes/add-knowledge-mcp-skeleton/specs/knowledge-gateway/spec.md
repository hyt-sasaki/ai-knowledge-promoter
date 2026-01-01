## ADDED Requirements

### Requirement: HTTP Health Check for Cloud Run
MCPサーバーはCloud Runのヘルスチェック用にHTTPエンドポイントを提供しなければならない（SHALL）。
このエンドポイントはMCPツールとは別に、FastMCPの`@custom_route`デコレータで実装される通常のHTTP/1エンドポイントである。

#### Scenario: ヘルスチェック成功
- **WHEN** GET /health にHTTPリクエストを送信する
- **THEN** ステータスコード200が返される
- **AND** レスポンスボディに `{"status": "healthy"}` が含まれる

### Requirement: Save Knowledge Tool
MCPサーバーは `save_knowledge` ツールを提供しなければならない（SHALL）。
Local Agentがナレッジを保存するためのエントリポイントとなる。

#### Scenario: ナレッジ保存成功（Phase 1スタブ）
- **WHEN** `save_knowledge` ツールが呼び出される
- **AND** content パラメータが提供される
- **THEN** 成功レスポンスが返される
- **AND** 保存されたナレッジのIDが返される

#### Scenario: ナレッジ保存失敗（必須パラメータ不足）
- **WHEN** `save_knowledge` ツールが呼び出される
- **AND** content パラメータが空または未提供
- **THEN** エラーレスポンスが返される
- **AND** エラーメッセージに「content is required」が含まれる

### Requirement: Search Knowledge Tool
MCPサーバーは `search_knowledge` ツールを提供しなければならない（SHALL）。
Local Agentが蓄積されたナレッジを検索するためのエントリポイントとなる。

#### Scenario: ナレッジ検索成功（Phase 1スタブ）
- **WHEN** `search_knowledge` ツールが呼び出される
- **AND** query パラメータが提供される
- **THEN** 成功レスポンスが返される
- **AND** 検索結果のリスト（空可）が返される

#### Scenario: ナレッジ検索失敗（必須パラメータ不足）
- **WHEN** `search_knowledge` ツールが呼び出される
- **AND** query パラメータが空または未提供
- **THEN** エラーレスポンスが返される
- **AND** エラーメッセージに「query is required」が含まれる

### Requirement: Cloud Run Deployment
MCPサーバーはCloud Run上でホスティングされなければならない（SHALL）。

#### Scenario: Cloud Runデプロイ成功
- **WHEN** MCPサーバーがCloud Runにデプロイされる
- **THEN** サービスが正常に起動する
- **AND** ヘルスチェックが成功する
- **AND** MCPツール呼び出しが可能になる

### Requirement: Local Agent MCP Connection
Local Agent（Claude Code）はMCPサーバーに接続できなければならない（SHALL）。

#### Scenario: MCP接続成功
- **WHEN** Claude CodeがMCPサーバーに接続を試みる
- **THEN** 接続が確立される
- **AND** 利用可能なツール一覧が取得できる

---

## Phase 2 Requirements

### Requirement: Cloud Run Authentication
MCPサーバーは認証されたリクエストのみを受け付けなければならない（SHALL）。

#### Scenario: 認証成功
- **WHEN** Authorization: Bearer <valid-token> ヘッダー付きでリクエストを送信する
- **THEN** リクエストが処理される
- **AND** 正常なレスポンスが返される

#### Scenario: 認証失敗（トークンなし）
- **WHEN** Authorization ヘッダーなしでリクエストを送信する
- **THEN** ステータスコード401または403が返される

### Requirement: Firestore Persistence
ナレッジはFirestoreに永続化されなければならない（SHALL）。

#### Scenario: ナレッジ保存成功（Firestore）
- **WHEN** `save_knowledge` ツールが呼び出される
- **AND** title, content パラメータが提供される
- **THEN** Firestoreにドキュメントが作成される
- **AND** 作成されたドキュメントのIDが返される
- **AND** created_at, updated_at タイムスタンプが設定される

### Requirement: Knowledge Data Model
ナレッジドキュメントは以下のフィールドを持たなければならない（SHALL）。

| フィールド | 型 | 必須 | 説明 |
|-----------|------|------|------|
| id | string | Yes | ドキュメントID（Firestore自動生成） |
| title | string | Yes | ナレッジのタイトル |
| content | string | Yes | ナレッジの本文 |
| user_id | string | Yes | ユーザー識別子 |
| source | string | Yes | "personal" または "team" |
| status | string | Yes | "draft", "proposed", "promoted" のいずれか |
| tags | array | No | タグのリスト |
| schema_version | number | Yes | スキーマバージョン（初期値: 1） |
| created_at | timestamp | Yes | 作成日時 |
| updated_at | timestamp | Yes | 更新日時 |

### Requirement: Search by Title Prefix
タイトル前方一致検索ができなければならない（SHALL）。

#### Scenario: タイトル前方一致検索成功
- **WHEN** `search_knowledge` ツールが呼び出される
- **AND** query パラメータに検索文字列が提供される（#で始まらない）
- **THEN** タイトルが query で始まるナレッジが返される
- **AND** 結果は limit パラメータで指定された件数以下

### Requirement: Search by Tag
タグ検索ができなければならない（SHALL）。

#### Scenario: タグ検索成功
- **WHEN** `search_knowledge` ツールが呼び出される
- **AND** query パラメータに "#tagname" 形式で提供される
- **THEN** tags フィールドに "tagname" を含むナレッジが返される
- **AND** 結果は limit パラメータで指定された件数以下
