## MODIFIED Requirements

### Requirement: Save Knowledge Tool
MCPサーバーは `save_knowledge` ツールを提供しなければならない（SHALL）。
Local Agentがナレッジを保存するためのエントリポイントとなる。
ナレッジはVector Search 2.0 Collectionに永続化される。

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
- **THEN** ナレッジがVector Search 2.0 Collectionに保存される
- **AND** 成功レスポンスが返される
- **AND** 保存されたナレッジのIDが返される
- **AND** created_at タイムスタンプが自動付与される
- **AND** updated_at タイムスタンプが自動付与される
- **AND** user_id: "anonymous" が自動付与される
- **AND** Auto-Embeddingsによりベクトルが自動生成される

#### Scenario: ナレッジ保存失敗（必須パラメータ不足）
- **WHEN** `save_knowledge` ツールが呼び出される
- **AND** content パラメータが空または未提供
- **THEN** エラーレスポンスが返される
- **AND** エラーメッセージに「content is required」が含まれる

### Requirement: Search Knowledge Tool
MCPサーバーは `search_knowledge` ツールを提供しなければならない（SHALL）。
Local Agentが蓄積されたナレッジを検索するためのエントリポイントとなる。
検索はVector Search 2.0のセマンティック検索で実行される。

#### Scenario: ナレッジ検索成功
- **WHEN** `search_knowledge` ツールが呼び出される
- **AND** query パラメータが提供される
- **THEN** Vector Search 2.0からセマンティック検索が実行される
- **AND** 成功レスポンスが返される
- **AND** 検索結果のリスト（空可）が返される
- **AND** 各結果にはid, title, content, score が含まれる
- **AND** scoreはセマンティック検索の類似度スコアを表す

#### Scenario: ナレッジ検索失敗（必須パラメータ不足）
- **WHEN** `search_knowledge` ツールが呼び出される
- **AND** query パラメータが空または未提供
- **THEN** エラーレスポンスが返される
- **AND** エラーメッセージに「query is required」が含まれる
