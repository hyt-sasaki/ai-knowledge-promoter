## ADDED Requirements

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
