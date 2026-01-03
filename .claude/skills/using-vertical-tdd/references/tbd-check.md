# spec.md TBDチェックワークフロー

## 目的

archive前にspec.mdの未定義箇所（TBD）を検出し、すべて解決されていることを確認します。TBDが残っている場合、archiveをブロックします。

## チェック対象

1. **正式版spec.md**: `openspec/specs/*/spec.md`
2. **change内spec.md**: `openspec/changes/<change-id>/specs/*/spec.md`

## TBDの定義

以下のパターンを「未定義箇所」として検出:

| パターン | 例 |
|---------|-----|
| `TBD` | Purpose: TBD |
| `tbd` | 説明: tbd |
| `To Be Determined` | Status: To Be Determined |
| `TODO:` | TODO: 詳細を定義 |
| `FIXME:` | FIXME: 仕様を確認 |

## チェック方法

### 手動チェック（grepコマンド）

```bash
# 正式版spec.mdのチェック
grep -rn -E "(TBD|tbd|To Be Determined|TODO:|FIXME:)" openspec/specs/*/spec.md

# change内spec.mdのチェック
grep -rn -E "(TBD|tbd|To Be Determined|TODO:|FIXME:)" openspec/changes/<change-id>/specs/*/spec.md

# 両方を一度にチェック
grep -rn -E "(TBD|tbd|To Be Determined|TODO:|FIXME:)" openspec/specs/*/spec.md openspec/changes/<change-id>/specs/*/spec.md
```

**期待される結果**: 結果なし（TBD箇所がない）

### AIによる自動検出プロンプト

エージェントに以下のタスクを依頼:

```
## タスク
以下のspec.mdファイルを解析し、未定義箇所（TBD）を検出してください。

## 入力
- openspec/specs/<capability>/spec.md
- openspec/changes/<change-id>/specs/<capability>/spec.md

## 検出対象
- TBD/tbd
- To Be Determined
- TODO: で始まるコメント
- FIXME: で始まるコメント
- 明らかに未完成なセクション（Purpose: TBD、説明文がないなど）

## 出力
- TBD箇所一覧（ファイル名、行番号、内容）
- 推奨修正案（可能であれば）
```

## ブロッキングルール

**重要**: TBD箇所が1つでもある場合、archiveを実行してはいけません。

### ブロッキング条件

- 正式版spec.mdにTBDが存在する
- change内spec.mdにTBDが存在する
- いずれかのパターン（TBD, tbd, To Be Determined, TODO:, FIXME:）にマッチする

### ブロック時の対応

1. TBD箇所を特定（上記のgrepコマンドで確認）
2. 適切な内容で置換
3. コミット（`docs: resolve TBD in spec.md`）
4. 再チェック
5. TBD箇所が0になったらarchiveに進む

## よくあるTBD箇所

| 箇所 | 例 | 修正方法 |
|------|-----|----------|
| Purpose | `Purpose: TBD` | 機能の目的を具体的に記述 |
| Scenario詳細 | `THEN: TBD` | 期待される結果を具体的に記述 |
| パラメータ説明 | `説明: TBD` | パラメータの説明を記述 |
| エラーケース | `エラー: TBD` | エラー条件と対応を記述 |

## 修正フロー

```
1. grepでTBD箇所を検出
   ↓
2. 各TBD箇所を確認
   ↓
3. 適切な内容で置換
   ↓
4. コミット: git commit -m "docs: resolve TBD in spec.md for <capability>"
   ↓
5. 再度grepでチェック
   ↓
6. 結果が空であることを確認
   ↓
7. archiveに進む
```

## コミット戦略

TBD解決のコミット:

```bash
git add openspec/specs/<capability>/spec.md
git add openspec/changes/<change-id>/specs/<capability>/spec.md
git commit -m "docs: resolve TBD in spec.md for <capability>"
```

詳細は [commit-strategy.md](commit-strategy.md) を参照。

## よくある質問

**Q: TBDを意図的に残したい場合は？**

A: archiveはブロッキングとなります。TBDを残したままarchiveする場合は、以下の選択肢を検討:
1. TBDを具体的な内容で置換する
2. 「未定義」であることを明示的に仕様として記述する（例: `この動作は実装依存とする`）
3. 該当要件を別changeに分離し、先に完成した部分のみarchiveする

**Q: Purpose: TBDはアーカイブ時に自動生成されるのでは？**

A: `openspec archive`コマンドは新規capability作成時にPurposeのプレースホルダーを生成しますが、archive前に適切な内容に置換する必要があります。プレースホルダーのままではarchiveがブロックされます。

**Q: design.mdやtasks.mdのTBDもチェックすべきか？**

A: このワークフローではspec.mdのみを対象とします。design.mdのOpen Questionsは別途 [step5-archive-release.md](step5-archive-release.md) のチェックリストで確認します。
