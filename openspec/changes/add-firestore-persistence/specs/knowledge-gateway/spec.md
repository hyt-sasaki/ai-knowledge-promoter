## MODIFIED Requirements

### Requirement: Save Knowledge Tool
MCPサーバーは `save_knowledge` ツールを提供しなければならない（SHALL）。
Local Agentがナレッジを保存するためのエントリポイントとなる。
ナレッジはFirestoreに永続化される。

#### Scenario: ナレッジ保存成功
- **WHEN** `save_knowledge` ツールが呼び出される
- **AND** content パラメータが提供される
- **THEN** ナレッジがFirestoreに保存される
- **AND** 成功レスポンスが返される
- **AND** 保存されたナレッジのIDが返される
- **AND** schema_version: 1 が自動付与される
- **AND** updated_at タイムスタンプが自動付与される

#### Scenario: ナレッジ保存失敗（必須パラメータ不足）
- **WHEN** `save_knowledge` ツールが呼び出される
- **AND** content パラメータが空または未提供
- **THEN** エラーレスポンスが返される
- **AND** エラーメッセージに「content is required」が含まれる

### Requirement: Search Knowledge Tool
MCPサーバーは `search_knowledge` ツールを提供しなければならない（SHALL）。
Local Agentが蓄積されたナレッジを検索するためのエントリポイントとなる。
検索はFirestoreの部分一致クエリで実行される。

#### Scenario: ナレッジ検索成功
- **WHEN** `search_knowledge` ツールが呼び出される
- **AND** query パラメータが提供される
- **THEN** Firestoreから部分一致検索が実行される
- **AND** 成功レスポンスが返される
- **AND** 検索結果のリスト（空可）が返される
- **AND** 各結果にはid, title, content, score が含まれる

#### Scenario: ナレッジ検索失敗（必須パラメータ不足）
- **WHEN** `search_knowledge` ツールが呼び出される
- **AND** query パラメータが空または未提供
- **THEN** エラーレスポンスが返される
- **AND** エラーメッセージに「query is required」が含まれる
