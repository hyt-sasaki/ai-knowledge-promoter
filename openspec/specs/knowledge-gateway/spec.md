# knowledge-gateway Specification

## Purpose
開発者が日々のコーディング中に得た断片的なナレッジを蓄積し、セマンティック検索で関連するナレッジを即座に発見できるようにするMCPサーバーを提供する。ナレッジはVector Search 2.0に永続化され、Auto-Embeddingsによるセマンティック検索が可能。
## Requirements
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
- **AND** 各結果には最低限 id, title, content, score が含まれる
- **AND** 各結果には tags, source, status も含まれる場合がある（実装依存）
- **AND** scoreはセマンティック検索の類似度スコアを表す

#### Scenario: ナレッジ検索失敗（必須パラメータ不足）
- **WHEN** `search_knowledge` ツールが呼び出される
- **AND** query パラメータが空または未提供
- **THEN** エラーレスポンスが返される
- **AND** エラーメッセージに「query is required」が含まれる

### Requirement: Delete Knowledge Tool
MCPサーバーは `delete_knowledge` ツールを提供しなければならない（SHALL）。
Local Agentがナレッジを削除するためのエントリポイントとなる。

#### Scenario: ナレッジ削除成功
- **WHEN** `delete_knowledge` ツールが呼び出される
- **AND** id パラメータが提供される
- **AND** 指定されたIDのナレッジが存在する
- **THEN** 成功レスポンスが返される
- **AND** ナレッジが削除される

#### Scenario: ナレッジ削除失敗（存在しないID）
- **WHEN** `delete_knowledge` ツールが呼び出される
- **AND** id パラメータが提供される
- **AND** 指定されたIDのナレッジが存在しない
- **THEN** エラーレスポンスが返される
- **AND** エラーメッセージに「knowledge not found」が含まれる

#### Scenario: ナレッジ削除失敗（必須パラメータ不足）
- **WHEN** `delete_knowledge` ツールが呼び出される
- **AND** id パラメータが空または未提供
- **THEN** エラーレスポンスが返される
- **AND** エラーメッセージに「id is required」が含まれる

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

### Requirement: Promote Knowledge Tool
MCPサーバーは `promote_knowledge` ツールを提供しなければならない（SHALL）。
個人ナレッジ（personal/draft）を提案状態（personal/proposed）に遷移させるエントリポイントとなる。

#### Parameters
| パラメータ | 必須 | 説明 |
|-----------|------|------|
| id | Yes | 昇格対象のナレッジID |

#### Scenario: ナレッジ昇格成功
- **WHEN** `promote_knowledge` ツールが呼び出される
- **AND** id パラメータが提供される
- **AND** 指定されたIDのナレッジが存在する
- **AND** ナレッジが personal/draft 状態である
- **THEN** ナレッジのステータスが "proposed" に更新される
- **AND** 成功レスポンスが返される
- **AND** 更新されたナレッジのIDとステータスが返される

#### Scenario: ナレッジ昇格失敗（存在しないID）
- **WHEN** `promote_knowledge` ツールが呼び出される
- **AND** id パラメータが提供される
- **AND** 指定されたIDのナレッジが存在しない
- **THEN** エラーレスポンスが返される
- **AND** エラーメッセージに「knowledge not found」が含まれる

#### Scenario: ナレッジ昇格失敗（昇格不可状態）
- **WHEN** `promote_knowledge` ツールが呼び出される
- **AND** ナレッジが personal/draft 以外の状態である
- **THEN** エラーレスポンスが返される
- **AND** エラーメッセージに「only draft knowledge can be promoted」が含まれる

#### Scenario: ナレッジ昇格失敗（必須パラメータ不足）
- **WHEN** `promote_knowledge` ツールが呼び出される
- **AND** id パラメータが空または未提供
- **THEN** エラーレスポンスが返される
- **AND** エラーメッセージに「id is required」が含まれる

### Requirement: Archive Knowledge on Promotion Complete
MCPサーバーは昇格完了時に元ナレッジをアーカイブしなければならない（SHALL）。
アーカイブは `archived_knowledge` コレクションへの移動として実装される。

※ 本要件の実際の呼び出しはPhase 4の同期エンドポイント（POST /sync）で実装される。Phase 3ではアーカイブ用のRepositoryとメソッドを準備する。

#### Scenario: 昇格完了時のアーカイブ
- **WHEN** 昇格PRがマージされる（Phase 4で実装）
- **AND** 同期エンドポイントが呼び出される
- **THEN** 元ナレッジが `knowledge` コレクションから削除される
- **AND** 元ナレッジが `archived_knowledge` コレクションに保存される
- **AND** promoted_to_id に新しいナレッジIDが設定される
- **AND** archived_at タイムスタンプが設定される

### Requirement: Repository Extended Search Methods
KnowledgeRepositoryは拡張検索メソッドを提供しなければならない（SHALL）。
GitHub連携とステータス管理のために必要。

#### Scenario: GitHub パスでナレッジ検索
- **WHEN** `find_by_github_path` メソッドが呼び出される
- **AND** 有効なGitHubパスが提供される
- **THEN** 該当するナレッジが返される
- **OR** 見つからない場合はNoneが返される

#### Scenario: PR URLでナレッジ検索
- **WHEN** `find_by_pr_url` メソッドが呼び出される
- **AND** 有効なPR URLが提供される
- **THEN** 該当するナレッジが返される
- **OR** 見つからない場合はNoneが返される

#### Scenario: ステータス更新
- **WHEN** `update_status` メソッドが呼び出される
- **AND** 有効なIDとステータスが提供される
- **THEN** ナレッジのステータスが更新される
- **AND** 更新されたナレッジが返される
- **AND** updated_at タイムスタンプが更新される

