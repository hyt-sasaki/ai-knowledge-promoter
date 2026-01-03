# Coverage Report: [change-id]

このファイルは、spec.mdの要件がverify.mdおよび自動テストでどの程度カバーされているかを記録します。

## 使い方

1. このテンプレートを `openspec/changes/<change-id>/coverage.md` にコピー
2. spec.mdの各RequirementとScenarioを抽出
3. verify.mdおよび自動テストとのマッピングを分析
4. カバレッジ状況を記録

詳細は [references/coverage-check.md](../references/coverage-check.md) を参照してください。

---

**Generated**: YYYY-MM-DD HH:MM:SS

## Summary

| Status | Count |
|--------|-------|
| Covered | X |
| Partially Covered | X |
| Not Covered | X |
| **Total** | **X** |

**Coverage Rate**: XX.X%

---

## Requirements Coverage

### Requirement: [要件名]

**Status**: Covered / Partially Covered / Not Covered (XX%)

| Scenario | verify.md | Unit Tests | Status |
|----------|-----------|------------|--------|
| [シナリオ名] | [test-name] | [test_function] | Covered |
| [シナリオ名] | - | - | **NOT COVERED** |

**Mapping Details**:

- **WHEN** [条件]
  - verify.md: `test-name` ([コマンドの説明])
  - Unit Test: `test_function` in `tests/test_xxx.py`
- **THEN** [期待結果]
  - verify.md: `test-name` 期待値: [期待値]
- **AND** [追加の期待結果]
  - Unit Test: `test_function` assertion

---

### Requirement: [次の要件名]

**Status**: Not Covered (0%)

| Scenario | verify.md | Unit Tests | Status |
|----------|-----------|------------|--------|
| [シナリオ名] | - | - | **NOT COVERED** |

**Action Required**:
- [ ] verify.mdにテストケースを追加
- [ ] または自動テストでカバー
- [ ] または「Auto-Test Targets」に記載

---

## Auto-Test Targets（自動テストでカバーすべき内容）

> **Note**: 以下のシナリオは自動テスト（ユニットテスト等）でカバーすべきです。
> verify.md（統合テスト）ではなく、各言語のテストフレームワークで実装します。

### Should be covered by Unit Tests

| Requirement | Scenario | Test Type | Reason |
|-------------|----------|-----------|--------|
| [要件名] | [シナリオ名] | Unit Test | 純粋関数・ビジネスロジック |
| [要件名] | [シナリオ名] | Unit Test | バリデーション |

### Expected Test Files

- `tests/test_xxx.py` - [テスト対象の説明]
- `tests/test_yyy.py` - [テスト対象の説明]

---

## Uncovered Items (Blocking)

> **Warning**: 以下の項目がカバーされていないため、次のステップに進めません。

- [ ] Requirement: [要件名] / Scenario: [シナリオ名]
- [ ] Requirement: [要件名] / Scenario: [シナリオ名]

**対応方法**:
1. verify.mdにテストケースを追加する
2. または自動テストでカバーする
3. または「Auto-Test Targets」に明示的に記載する（Step 4で対応予定として）

---

## Coverage Check History

| Step | Date | Status | Notes |
|------|------|--------|-------|
| Step 2 (verify.md作成後) | YYYY-MM-DD | Pass/Fail | [備考] |
| Step 3 (GREEN確認後) | YYYY-MM-DD | Pass/Fail | [備考] |
| Step 5 (Archive前) | YYYY-MM-DD | Pass/Fail | [備考] |

---

## Appendix: Extracted Requirements

> 参考: spec.mdから抽出したRequirementsとScenarios

### From spec.md

```
### Requirement: [要件名]
[説明]

#### Scenario: [シナリオ名]
- **WHEN** [条件]
- **THEN** [期待結果]
- **AND** [追加の期待結果]
```
