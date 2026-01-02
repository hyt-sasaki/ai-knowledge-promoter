## MODIFIED Requirements

### Requirement: Save Knowledge Tool
MCPサーバーは `save_knowledge` ツールを提供しなければならない（SHALL）。
Local Agentがナレッジを保存するためのエントリポイントとなる。
ナレッジはFirestoreに永続化される。

#### Parameters
| パラメータ | 必須 | 説明 |
|-----------|------|------|
| content | Yes | ナレッジ本文 |
| title | No | ナレッジのタイトル（未指定時はcontentの先頭30文字を使用） |
| tags | No | タグのリスト |

※ user_id はPhase 2では固定値 "anonymous" を使用。将来の認証統合時に実ユーザーIDに置換。

#### Scenario: ナレッジ保存成功
- **WHEN** `save_knowledge` ツールが呼び出される
- **AND** content パラメータが提供される
- **THEN** ナレッジがFirestoreに保存される
- **AND** 成功レスポンスが返される
- **AND** 保存されたナレッジのIDが返される
- **AND** schema_version: 1 が自動付与される
- **AND** updated_at タイムスタンプが自動付与される
- **AND** user_id: "anonymous" が自動付与される

#### Scenario: ナレッジ保存失敗（必須パラメータ不足）
- **WHEN** `save_knowledge` ツールが呼び出される
- **AND** content パラメータが空または未提供
- **THEN** エラーレスポンスが返される
- **AND** エラーメッセージに「content is required」が含まれる

### Requirement: Search Knowledge Tool
MCPサーバーは `search_knowledge` ツールを提供しなければならない（SHALL）。
Local Agentが蓄積されたナレッジを検索するためのエントリポイントとなる。
検索はFirestoreの前方一致クエリで実行される。

#### Scenario: ナレッジ検索成功
- **WHEN** `search_knowledge` ツールが呼び出される
- **AND** query パラメータが提供される
- **THEN** Firestoreから前方一致検索が実行される
- **AND** 成功レスポンスが返される
- **AND** 検索結果のリスト（空可）が返される
- **AND** 各結果にはid, title, content が含まれる
- **AND** scoreは将来のVertex AI Search用でありFirestoreではnullとなる

#### Scenario: ナレッジ検索失敗（必須パラメータ不足）
- **WHEN** `search_knowledge` ツールが呼び出される
- **AND** query パラメータが空または未提供
- **THEN** エラーレスポンスが返される
- **AND** エラーメッセージに「query is required」が含まれる
