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
