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

## 各ステップでのコミットポイント

垂直TDD各ステップでの具体的なコミットポイントは、各ワークフローファイルを参照してください：

- [Step 0: Proposal](step0-proposal.md#コミット戦略)
- [Step 0.5: Tech Spike](step0.5-tech-spike.md#コミット戦略)
- [Step 0.9: Design](step0.9-design.md#コミット戦略)
- [Step 1: Runbook & Red](step1-runbook-red.md#コミット戦略)
- [Step 2: Skeleton Green](step2-skeleton-green.md#コミット戦略)
- [Step 3: Logic Meat](step3-logic-meat.md#コミット戦略)
- [Step 4: Archive & Release](step4-archive-release.md#コミット戦略)

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
