# verify.md / coverage.md 正式版昇格ワークフロー

## 目的

archive完了時にverify.mdとcoverage.mdを正式版として`specs/<capability>/`に昇格し、既存ファイルがある場合はインテリジェントにマージします。

## 配置場所

### verify.md
- **昇格前**: `openspec/changes/<change-id>/verify.md`
- **昇格後**: `openspec/specs/<capability>/verify.md`

### coverage.md
- **昇格前**: `openspec/changes/<change-id>/coverage.md`
- **昇格後**: `openspec/specs/<capability>/coverage.md`

## 昇格手順

### Step 1: 対象ファイルの確認

```bash
# change内のverify.mdとcoverage.mdを確認
ls openspec/changes/<change-id>/verify.md
ls openspec/changes/<change-id>/coverage.md

# 対象capabilityの確認
ls openspec/changes/<change-id>/specs/
```

### Step 2: 既存ファイルの確認

```bash
# 正式版verify.md/coverage.mdの存在確認
for cap in $(ls openspec/changes/<change-id>/specs/); do
  echo "=== $cap ==="
  if [ -f "openspec/specs/$cap/verify.md" ]; then
    echo "Existing verify.md found: openspec/specs/$cap/verify.md → マージ必要"
  else
    echo "No existing verify.md: openspec/specs/$cap/verify.md → 新規昇格"
  fi
  if [ -f "openspec/specs/$cap/coverage.md" ]; then
    echo "Existing coverage.md found: openspec/specs/$cap/coverage.md → 更新必要"
  else
    echo "No existing coverage.md: openspec/specs/$cap/coverage.md → 新規昇格"
  fi
done
```

### Step 3a: 既存ファイルなし（新規昇格）

```bash
# verify.mdを正式版にコピー
cp openspec/changes/<change-id>/verify.md openspec/specs/<capability>/verify.md

# coverage.mdを正式版にコピー
cp openspec/changes/<change-id>/coverage.md openspec/specs/<capability>/coverage.md
```

### Step 3b: 既存verify.mdあり（マージ必要）

後述の「verify.mdマージロジック」に従ってマージを実行します。

### Step 3c: 既存coverage.mdあり（更新必要）

後述の「coverage.md更新ロジック」に従って更新を実行します。

### Step 4: マージ後カバレッジ確認

正式版spec.mdと正式版verify.mdでカバレッジを確認し、coverage.mdを最終更新します。

### Step 5: 昇格コミット

```bash
git add openspec/specs/<capability>/verify.md
git add openspec/specs/<capability>/coverage.md
git commit -m "docs: promote verify.md and coverage.md to specs/<capability>"
```

## verify.mdマージロジック

### セクション構造の保持

verify.mdの標準構造:

```markdown
1. 環境変数（Setup）
2. Normal Path（正常系テスト）
3. Edge Cases（異常系テスト）
4. （オプション）その他のテストセクション
```

この構造を維持しながらマージします。

### Runme.devにおける順序の重要性

Runme.devでは`runme run --all`でテストを順次実行します。順序が動作に影響するため、マージ時は以下を考慮:

1. **Setup順序**: 依存関係のあるsetupは順序を維持
2. **テスト順序**: 前のテストの結果を参照するテストがある場合、順序維持
3. **runme run --allからの除外**: 特定のテストは`excludeFromRunAll`属性で除外

### excludeFromRunAll属性の活用

二重実行を防ぐため、以下のパターンを使用:

```markdown
<!-- README.mdまたは親ファイルで一括実行を定義 -->
```sh {"name":"verify-all"}
runme run --all --filename verify.md
```

<!-- verify.md内の手動実行用コマンドは除外 -->
```sh {"excludeFromRunAll":"true","name":"manual-test"}
# このコマンドはrunme run --allから除外される
```
```

参考例: `openspec/changes/archive/2026-01-01-add-knowledge-mcp-skeleton/` の構造

### マージパターン

マージには3つの主要パターンがあります:

#### パターン1: 新規テスト追加

新しいシナリオに対応するテストを追加する場合:

| セクション | マージ順序 | 理由 |
|-----------|-----------|------|
| **環境変数/Setup** | 既存 → 新規 | 既存のセットアップが先に実行される必要がある場合が多い |
| **Normal Path** | 既存 → 新規 | 基本機能テスト後に拡張機能テスト |
| **Edge Cases** | 既存 → 新規 | 基本エラーケース後に新規エラーケース |

#### パターン2: 既存テストの拡張・微調整

同じシナリオが拡張される場合、既存のコマンドを微調整:

**ケース例**:
- APIのパラメータが追加された → 既存テストにパラメータを追加
- レスポンス形式が拡張された → 期待値コメントを更新
- エンドポイントURLが変更された → 既存テストのURLを修正
- 認証方式が追加された → ヘッダーを追加

**微調整の方法**:
```markdown
<!-- 既存テスト -->
```sh {"name":"test-save-knowledge"}
curl -s -X POST "${SERVICE_URL}/mcp" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test"}'
# 期待値: {"status": "saved"}
```

<!-- 拡張後（パラメータ追加、期待値更新） -->
```sh {"name":"test-save-knowledge"}
curl -s -X POST "${SERVICE_URL}/mcp" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${TOKEN}" \  # 認証ヘッダー追加
  -d '{"title": "Test", "tags": ["new"]}'  # パラメータ追加
# 期待値: {"status": "saved", "id": "...", "tags": ["new"]}  # 期待値拡張
```
```

**微調整のルール**:
1. テスト名（`{"name":"..."}`）は変更しない
2. 既存のアサーション/期待値は拡張のみ（削除しない）
3. 後方互換性を意識（既存の期待値は引き続き満たす）
4. 変更理由をコメントで明記

#### パターン3: テスト置換

シナリオが根本的に変更された場合、既存テストを新規テストで置換:

**ケース例**:
- 既存機能が廃止され、新機能に置き換わった
- テスト対象のAPIが完全に再設計された

**置換のルール**:
1. 既存テストをコメントアウトまたは削除
2. 新規テストを同じ位置に配置
3. 可能であれば同じテスト名を維持（`{"name":"..."}`）
4. 置換理由をPRで明記

### マージアルゴリズム

```
Input: existing_verify.md, new_verify.md
Output: merged_verify.md

1. 両ファイルからセクションを解析
2. 各セクションについて:
   a. 既存と新規のコードブロックを抽出
   b. 名前競合を検出
   c. 競合解決パターンを判定:
      - 同名で内容が異なる場合 → パターン2（微調整）またはパターン3（置換）を検討
      - 新規テストのみの場合 → パターン1（追加）
   d. セクションルールに従ってマージ
3. excludeFromRunAll属性を適切に設定
4. マージ結果を生成
5. 競合・変更箇所にはレビューマーカーを付与
```

### 名前競合解決

同名のコードブロック（`{"name":"test-xxx"}`）がある場合:

1. **内容比較**: 既存と新規の内容を比較
2. **判定**:
   - 軽微な差分 → パターン2（既存を微調整）
   - 大きな差分 → パターン3（置換）またはサフィックス追加
3. **対話的解決**: 判断が難しい場合はユーザーに確認

```markdown
<!-- CONFLICT: 同名のテストブロックが存在します -->
<!-- 既存: test-health (基本ヘルスチェック) -->
<!-- 新規: test-health (拡張ヘルスチェック) -->
<!-- 推奨: 既存テストを新規内容で更新（パターン2: 微調整） -->
```

## エージェント向けマージプロンプト

エージェントにマージを依頼する際のプロンプト:

```
## タスク
2つのverify.mdファイルをマージし、正式版verify.mdを生成してください。

## 入力
1. 既存verify.md: openspec/specs/<capability>/verify.md
2. 新規verify.md: openspec/changes/<change-id>/verify.md

## マージルール

### パターン判定
同名のテストブロックがある場合:
- 内容が軽微に異なる → 既存テストを微調整（パターン2）
- 内容が大きく異なる → 置換またはサフィックス追加（パターン3）
- 新規テストのみ → 既存の後に追加（パターン1）

### セクション構造
1. セクション構造（環境変数/Setup → Normal Path → Edge Cases → その他）を維持
2. Setup/環境変数: 既存の後に新規を追加（重複する名前のブロックは統合）
3. Normal Path/Edge Cases: 既存テストの後に新規テストを追加

### 微調整（パターン2）のルール
シナリオが拡張される場合、既存コマンドを微調整:
- テスト名（{"name":"..."}）は維持
- パラメータ、ヘッダー、期待値を拡張
- 後方互換性を意識（既存の期待値は満たす）
- 変更箇所にコメントを追加

### 競合解決
名前競合がある場合:
- まず微調整（パターン2）を検討
- 微調整不可の場合は置換（パターン3）またはサフィックス追加
- 判断が難しい場合はコメントで選択肢を提示

## Runme.dev属性の扱い
1. `{"name":"..."}` は必須。すべてのコードブロックに設定
2. 手動実行用/参考用のコマンドには `{"excludeFromRunAll":"true"}` を追加
3. verify.md内にverify-allセクションは不要（README.mdで管理）

## 出力
- マージ後のverify.md内容
- 競合・微調整箇所にはレビュー用コメント付き
- 変更理由の説明

## 注意事項
- Runme.devのJSON形式セル設定を維持（{"name":"..."}）
- コードブロックの言語指定（sh, bash, python等）を維持
- 期待値コメントを保持・拡張
- 二重実行を防ぐためexcludeFromRunAll属性を適切に使用
```

## マージ後チェックリスト

マージ完了後に確認:

- [ ] セクション構造が正しい（Setup → Normal Path → Edge Cases → その他）
- [ ] すべてのコードブロックに`{"name":"..."}`属性がある
- [ ] 名前の重複がない（競合は解決済み）
- [ ] 微調整箇所が適切に更新されている
- [ ] 手動実行用コマンドに`excludeFromRunAll`が設定されている
- [ ] Runme.dev形式が正しい（`runme list`で確認）
- [ ] 期待値コメントが適切に記述されている
- [ ] カバレッジ100%確認済み（正式版spec.mdに対して）

## マージ後カバレッジ確認

マージ後の正式版verify.mdで改めてカバレッジを確認:

### 確認コマンド

```bash
# verify.mdのテスト一覧を確認
runme list --filename openspec/specs/<capability>/verify.md

# 全テスト実行
runme run --all --filename openspec/specs/<capability>/verify.md
```

### カバレッジ分析プロンプト

エージェントにカバレッジ分析を依頼:

```
## タスク
正式版spec.mdと正式版verify.mdのカバレッジを分析してください。

## 入力
1. 正式版spec.md: openspec/specs/<capability>/spec.md
2. 正式版verify.md: openspec/specs/<capability>/verify.md

## 出力
- 各Requirementのカバレッジ状況（Covered/Partially Covered/Not Covered）
- Uncovered Items一覧
- カバレッジ率

## ブロッキングルール
- すべてのRequirementが「Covered」であること
- 「Uncovered Items」が空であること
```

### ブロッキングルール

- マージ後verify.mdが正式版spec.mdの全Scenarioをカバーしていること
- 「Uncovered Items」が0であること
- カバレッジ不足の場合はマージを見直し、テストを追加

詳細は [coverage-check.md](coverage-check.md) を参照。

## coverage.md更新ロジック

coverage.mdは正式版spec.mdと正式版verify.mdに基づいて再生成されるため、verify.mdのようなマージは不要です。代わりに、既存のcoverage.mdを新しい内容で置き換えます。

### 更新手順

1. **正式版ファイルを入力として使用**:
   - `openspec/specs/<capability>/spec.md`
   - `openspec/specs/<capability>/verify.md`（マージ後）

2. **カバレッジ分析を実行**:
   - spec.mdのすべてのRequirementsとScenariosを抽出
   - verify.mdのテストケースを抽出
   - マッピング分析を実行
   - coverage.mdを再生成

3. **正式版として配置**:
   ```bash
   # 生成されたcoverage.mdを正式版に配置
   cp openspec/changes/<change-id>/coverage.md openspec/specs/<capability>/coverage.md
   # または、直接正式版として生成
   ```

### 更新時の考慮事項

- **履歴の保持**: 既存coverage.mdの履歴はgitで追跡される
- **差分確認**: 更新前後のカバレッジ率の変化を確認
- **後方互換性**: 以前カバーされていた項目が引き続きカバーされていることを確認

### coverage.md生成プロンプト

```
## タスク
正式版spec.mdと正式版verify.mdに基づいてcoverage.mdを生成してください。

## 入力
1. 正式版spec.md: openspec/specs/<capability>/spec.md
2. 正式版verify.md: openspec/specs/<capability>/verify.md

## 出力
templates/coverage-template.md のフォーマットに従ったcoverage.mdを生成してください。

## 要件
- すべてのRequirementが「Covered」であること
- 「Uncovered Items」が空であること
- カバレッジ率が100%であること
```

## コミット戦略

### 新規昇格の場合

```bash
git add openspec/specs/<capability>/verify.md
git add openspec/specs/<capability>/coverage.md
git commit -m "docs: promote verify.md and coverage.md to specs/<capability>"
```

### マージの場合

```bash
git add openspec/specs/<capability>/verify.md
git add openspec/specs/<capability>/coverage.md
git commit -m "docs: merge and promote verify.md and coverage.md to specs/<capability>"
```

詳細は [commit-strategy.md](commit-strategy.md) を参照。

## よくある質問

**Q: 複数のcapabilityにまたがるchangeの場合は？**

A: 各capabilityに対して個別にverify.mdを昇格します。changeのverify.mdがcapability単位で分割されていない場合は、マージ時に適切に分割してください。

**Q: マージ結果に問題がある場合は？**

A: マージはエージェントによるインテリジェントなアプローチで行われるため、結果をレビューして必要に応じて手動で調整してください。

**Q: 順序を完全にカスタマイズしたい場合は？**

A: エージェントにマージを依頼する際に、具体的な順序要件を指示してください。Runme.devでは順序が動作に影響するため、柔軟な調整が可能です。

**Q: 既存テストを微調整すべきか、新規追加すべきか判断が難しい場合は？**

A: 以下の基準で判断:
- 同じシナリオの拡張 → 微調整（パターン2）
- 別のシナリオ → 新規追加（パターン1）
- シナリオが根本的に変更 → 置換（パターン3）
判断が難しい場合はエージェントに選択肢を提示させ、ユーザーが決定します。

**Q: verify-allはどこに配置すべきか？**

A: verify.md自体には配置せず、README.mdや親ディレクトリで`runme run --all --filename verify.md`として管理します。これにより二重実行を防ぎます。参考: `openspec/changes/archive/2026-01-01-add-knowledge-mcp-skeleton/README.md`
