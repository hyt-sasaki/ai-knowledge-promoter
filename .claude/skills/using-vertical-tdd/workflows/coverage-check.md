# カバレッジチェックワークフロー

## 目的

spec.mdに記述された要件（Requirements）と各Scenarioが、verify.mdおよび自動テストで適切にカバーされているかをAIが自動分析し、coverage.mdを生成します。カバー漏れがある場合は次のステップに進めません（ブロッキング）。

## 実行タイミング

| ステップ | タイミング | 目的 |
|----------|-----------|------|
| Step 2 | verify.md作成後 | 統合テストのカバレッジ確認 |
| Step 3 | GREEN確認後 | スケルトン実装後の再確認 |
| Step 5 | Archive前 | ユニットテスト含む最終確認 |

## 配置場所

`openspec/changes/<change-id>/coverage.md`

## カバレッジチェック手順

### Step 1: spec.mdの解析

AIがspec.mdを読み込み、RequirementsとScenariosを抽出します。

**抽出対象**:
- `### Requirement:` ヘッダーから要件名を抽出
- `#### Scenario:` ヘッダーからシナリオ名を抽出
- `- **WHEN**`, `- **THEN**`, `- **AND**` から条件と期待結果を抽出

**出力形式（内部処理用）**:
```
Requirement 1: [要件名]
  Scenario 1-1: [シナリオ名]
    WHEN: [条件]
    THEN: [期待結果]
    AND: [追加の期待結果]
  Scenario 1-2: ...

Requirement 2: ...
```

### Step 2: verify.mdの解析

AIがverify.mdを読み込み、テストケースを抽出します。

**抽出対象**:
- `{"name":"xxx"}` からテスト名を抽出
- コードブロック内のコマンドを抽出
- `# 期待値:` コメントから期待結果を抽出
- セクション（Normal Path / Edge Cases等）を記録

### Step 3: 自動テストの解析（Step 5のみ）

AIが自動テストファイルを読み込み、テスト関数を抽出します。

**抽出対象**:
- テスト関数名（`test_xxx`, `def test_xxx`, `it('xxx')` 等）
- アサーション内容
- テスト対象の機能

### Step 4: マッピング分析

AIがspec.mdの各ScenarioとテストケースのマッピングをOを分析します。

**分析基準**:
1. **キーワードマッチング**: Scenario内のWHEN/THEN/ANDの内容とテストコマンド・期待値を比較
2. **セマンティックマッチング**: エンドポイント、HTTPメソッド、パラメータ、期待レスポンスの一致を分析
3. **カバレッジステータス判定**:
   - **Covered**: すべてのTHEN/ANDがテストで検証されている
   - **Partially Covered**: 一部のTHEN/ANDがテストで検証されている
   - **Not Covered**: テストが存在しない

### Step 5: coverage.md生成

[../templates/coverage-template.md](../templates/coverage-template.md) に従ってcoverage.mdを生成します。

## ブロッキングルール

### Step 2（verify.md作成後）

以下のいずれかを満たす必要があります：

1. すべてのScenarioが「Covered」または「Partially Covered」
2. 「Not Covered」のScenarioは「Auto-Test Targets」セクションに明示的に記載されている

### Step 3（GREEN確認後）

Step 2と同じルールを適用します。

### Step 5（Archive前）

以下のすべてを満たす必要があります：

1. 「Uncovered Items」セクションが空である
2. 「Auto-Test Targets」に記載された項目は自動テストでカバー済みである
3. すべてのRequirementが「Covered」

## AIプロンプト

### カバレッジ分析プロンプト

以下のプロンプトを使用してAIにカバレッジ分析を依頼します：

```
## タスク
spec.mdの要件とverify.md（および自動テスト）のカバレッジを分析し、coverage.mdを生成してください。

## 入力ファイル
1. spec.md: [パスを指定]
2. verify.md: [パスを指定]
3. 自動テストファイル（任意）: [パスを指定]

## 分析手順
1. spec.mdからすべてのRequirementsとScenariosを抽出
2. verify.mdからすべてのテストケースを抽出
3. 自動テストファイルからテスト関数を抽出（指定された場合）
4. 各ScenarioのWHEN/THEN/ANDとテストケースをマッピング
5. カバレッジステータスを判定（Covered/Partially Covered/Not Covered）
6. coverage.mdを生成

## 出力
templates/coverage-template.md のフォーマットに従ったcoverage.mdを生成してください。

## 注意事項
- 曖昧なマッピングは「Partially Covered」または「Needs Review」として記録
- verify.md（統合テスト）とUnit Testの両方を考慮
- 純粋関数やバリデーションロジックは「Auto-Test Targets」として推奨
- 「Uncovered Items」がある場合は明確に警告
```

## 各ステップでの実行方法

### Step 2: verify.md作成後

```
verify.md作成が完了しました。カバレッジチェックを実行します。

1. spec.mdとverify.mdを読み込み
2. カバレッジ分析を実行
3. coverage.mdを生成
4. 未カバー項目を確認

[coverage.md生成結果を表示]

未カバー項目がある場合：
- verify.mdにテストケースを追加する
- または「Auto-Test Targets」セクションに記載する（Step 4で自動テストとして実装予定）
```

### Step 3: GREEN確認後

```
スケルトン実装でGREEN確認が完了しました。カバレッジを再チェックします。

1. coverage.mdを再生成
2. すべてのScenarioがカバーされていることを確認

[coverage.md更新結果を表示]
```

### Step 5: Archive前

```
Archive前の最終カバレッジチェックを実行します。

1. spec.md、verify.md、自動テストファイルを読み込み
2. カバレッジ分析を実行
3. coverage.mdを最終更新
4. 「Uncovered Items」が空であることを確認
5. 「Auto-Test Targets」の項目が自動テストでカバーされていることを確認

[coverage.md最終結果を表示]

すべてのScenarioがカバーされていることを確認後、Archiveを実行します。
```

## よくある質問

**Q: 完全な自動マッチングは可能か？**

A: AIによるセマンティック分析を使用しますが、完全な自動マッチングは困難です。曖昧な場合は「Needs Review」として人間の確認を促します。

**Q: verify.mdと自動テストの両方が必要か？**

A: 状況によります。
- **統合テスト（verify.md）**: End-to-Endフロー、外部依存
- **ユニットテスト**: ビジネスロジック、純粋関数、バリデーション

テストピラミッドに従い、適切な分担を行います。

**Q: 「Auto-Test Targets」に記載したら、Step 2で「Not Covered」でも進めるか？**

A: はい。「Auto-Test Targets」に明示的に記載し、Step 4で自動テストとして実装することを約束すれば、Step 2/3では「Not Covered」でも進めます。ただし、Step 5では自動テストでカバーされている必要があります。

**Q: カバレッジ100%が必須か？**

A: spec.mdに記載されたすべてのScenarioがカバーされている必要があります。ただし、verify.mdまたは自動テストのいずれかでカバーされていればOKです。

## コミット戦略

coverage.md生成後のコミット：

```bash
git add openspec/changes/<change-id>/coverage.md
git commit -m "docs: add coverage report for <change-id>"
```

詳細は [commit-strategy.md](commit-strategy.md) を参照。
