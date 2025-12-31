# コミット戦略

## 原則：安定チェックポイントでのコミット

✅ **すべての安定状態でコミット**:
- 「commit when ready」ではなく「commit at every stable checkpoint」
- コードが動作確認できた時点で即コミット
- 次の作業に進む前に必ずコミット

❌ **大きなコミットを避ける**:
- 複数の機能を1つのコミットに含めない
- 「後でまとめてコミット」は禁止

## コミットメッセージ

[Conventional Commits](https://www.conventionalcommits.org/) に従います。

## PR戦略

柔軟な4-5PRで段階的マージ:

| PR | ブランチ命名 | タイミング | 必須/任意 |
|---|---|---|---|
| PR #1 | `proposal/<change-id>` | Step 1完了後 | 必須 |
| PR #1.5 | `design/<change-id>` | Step 1a/1b完了後 | 任意 |
| PR #2 | `skeleton/<change-id>` | Step 3完了後 | 必須 |
| PR #3 | `logic/<change-id>` | Step 4完了後 | 必須 |
| PR #4 | `release/<change-id>` | Step 5完了後 | 必須 |

## 各ステップでのコミットポイント

垂直TDD各ステップでの具体的なコミットポイントは、各ワークフローファイルを参照してください：

- [Step 1: Proposal](step1-proposal.md#コミット戦略) → **PR #1**
- [Step 1a: Tech Spike](step1a-tech-spike.md#コミット戦略)
- [Step 1b: Design](step1b-design.md#コミット戦略) → **PR #1.5**（任意）
- [Step 2: Runbook & Red](step2-runbook-red.md#コミット戦略)
- [Step 3: Skeleton Green](step3-skeleton-green.md#コミット戦略) → **PR #2**
- [Step 4: Logic Meat](step4-logic-meat.md#コミット戦略) → **PR #3**
- [Step 5: Archive & Release](step5-archive-release.md#コミット戦略) → **PR #4**

## よくある質問

**Q: すべてのステップでコミットすると、コミット履歴が大量になりませんか？**

A: はい、コミット数は増えます。しかし、各コミットが即座の復元ポイントになります。必要なら `git rebase -i` で後からスカッシュ可能です。

**Q: PR作成前にスカッシュすべきですか？**

A: プロジェクトのポリシー次第ですが、推奨は**スカッシュしない**：
- 各コミットが意味のあるチェックポイント
- レビュワーが段階的な進捗を理解しやすい
- 問題発生時のピンポイントリバートが可能

## 参考リソース

- [Conventional Commits](https://www.conventionalcommits.org/)
- [DORA Version Control Capability](https://dora.dev/capabilities/version-control/)
