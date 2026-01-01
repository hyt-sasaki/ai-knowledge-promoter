# Change: 知識共有MCPサーバーの垂直スケルトン構築

## 検証

### プロジェクトルートから実行

```bash
runme run --all --filename openspec/changes/add-knowledge-mcp-skeleton/verify.md
```

### このディレクトリから実行

```sh {"name":"verify-all"}
runme run --all --filename verify.md
```

### 個別のテストを実行

```bash
# 利用可能なテスト一覧
runme list --filename verify.md

# 個別実行
runme run setup-env --filename verify.md
runme run test-health --filename verify.md
runme run test-health-body --filename verify.md
```

詳細は `verify.md` を参照してください。
