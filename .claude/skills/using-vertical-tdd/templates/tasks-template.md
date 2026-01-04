# Tasks: [変更の簡潔な説明]

> ⚠️ **このタスクは using-vertical-tdd スキルに従って作業しています**
>
> 再開時は必ず `.claude/skills/using-vertical-tdd/SKILL.md` を参照してください。
> 各ステージの詳細ワークフローは下記リンクを確認してください。

パターン: [A: アプリケーション型 / B: インフラ先行型]

---

## 0. 提案フェーズ（Stage 1: Creating Changes）

> 📖 参照: [step1-proposal.md](.claude/skills/using-vertical-tdd/workflows/step1-proposal.md)

| Branch | `proposal/<change-id>` |
|--------|------------------------|

- [ ] proposal.md作成
- [ ] tasks.md作成
- [ ] spec delta作成
- [ ] `openspec validate <change-id> --strict`
- [ ] **PR #1作成**

---

## 1. 技術検証（任意: Stage 1）

> 📖 参照: [step1a-tech-spike.md](.claude/skills/using-vertical-tdd/workflows/step1a-tech-spike.md)

| Branch | `spike/<change-id>` |
|--------|---------------------|

- [ ] spike/results.md作成
- [ ] **PR #1a作成**

---

## 2. 設計（任意: Stage 1）

> 📖 参照: [step1b-design.md](.claude/skills/using-vertical-tdd/workflows/step1b-design.md)

| Branch | `design/<change-id>` |
|--------|----------------------|

- [ ] design.md作成
- [ ] **PR #1b作成**

---

## 3. インフラ基盤整備（パターンBのみ: Stage 2）

> 📖 参照: [step3-skeleton-green.md](.claude/skills/using-vertical-tdd/workflows/step3-skeleton-green.md)

| Branch | `infra/<change-id>` |
|--------|---------------------|

- [ ] インフラ構築
- [ ] **PR #2a作成**

---

## 4. スケルトン実装（Stage 2）

> 📖 参照: [step2-runbook-red.md](.claude/skills/using-vertical-tdd/workflows/step2-runbook-red.md), [step3-skeleton-green.md](.claude/skills/using-vertical-tdd/workflows/step3-skeleton-green.md)

| Branch | `feat/<change-id>` |
|--------|-------------------|

- [ ] verify.md作成（Runme.dev形式）
- [ ] REDステータス確認
- [ ] スケルトン実装
- [ ] GREENステータス確認
- [ ] **PR #2 (または #2b) 作成**

---

## 5. ロジック実装（Stage 2）

> 📖 参照: [step4-logic-meat.md](.claude/skills/using-vertical-tdd/workflows/step4-logic-meat.md)

| Branch | `feat/<change-id>-logic` |
|--------|--------------------------|

- [ ] テストケース合意（assert Falseパターン）
- [ ] ユニットTDD実装（Red-Green-Refactor）
- [ ] **PR #3作成**

---

## 6. アーカイブ・リリース（Stage 3）

> 📖 参照: [step5-archive-release.md](.claude/skills/using-vertical-tdd/workflows/step5-archive-release.md)

| Branch | `release/<change-id>` |
|--------|----------------------|

- [ ] 全テスト検証
- [ ] `openspec archive <change-id> --yes`
- [ ] verify.md / coverage.md正式版昇格
- [ ] フィーチャーフラグ有効化
- [ ] **PR #N作成**
