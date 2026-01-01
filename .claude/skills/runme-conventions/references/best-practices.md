# Runme.devベストプラクティス

## 目次

- [フォーマット規約](#フォーマット規約)
- [コードブロック設計](#コードブロック設計)
- [ドキュメント構成](#ドキュメント構成)
- [よくあるパターン](#よくあるパターン)

## フォーマット規約

### コミット前のフォーマット

VSCode拡張機能との差分を防ぐため、コミット前に必ず`runme fmt`を実行:

```bash
runme fmt -w --filename <target.md>
```

### 複数ファイルのフォーマット

```bash
# 特定ディレクトリ配下のすべてのmdファイル
find . -name "*.md" -exec runme fmt -w --filename {} \;
```

## コードブロック設計

### 命名規則

- **明確で短い名前**: `deploy`, `test`, `build`
- **ハイフン区切り**: `run-tests`, `build-docker`
- **動詞から始める**: `install-deps`, `start-server`

### 危険なコマンドの保護

破壊的なコマンドは`excludeFromRunAll`で保護:

```bash {"excludeFromRunAll":"true","name":"cleanup-all"}
rm -rf dist/ node_modules/
```

### 長時間実行プロセス

サーバー起動などは`background`を使用:

```bash {"background":"true","name":"dev-server"}
npm run dev
```

## ドキュメント構成

### verify.mdの構成例

```markdown
# 検証手順

## 前提条件

```bash {"name":"check-deps"}
node --version && npm --version
```

## ビルド

```bash {"name":"build"}
npm run build
```

## テスト

```bash {"name":"test"}
npm test
```

## クリーンアップ（オプション）

```bash {"excludeFromRunAll":"true","name":"clean"}
rm -rf dist/
```
```

### README.mdでの使用

セットアップ手順を実行可能に:

```markdown
## Getting Started

```bash {"name":"install"}
npm install
```

```bash {"name":"start"}
npm start
```
```

## よくあるパターン

### サブディレクトリでの実行

モノレポ構成で特定パッケージのコマンドを実行:

```bash {"cwd":"packages/api","name":"api-test"}
npm test
```

### 環境変数が必要なコマンド

```bash {"promptEnv":"yes","name":"deploy-prod"}
DEPLOY_ENV=production npm run deploy
```

### インタラクティブなコマンド

ユーザー入力が必要な場合:

```bash {"interactive":"true","name":"npm-login"}
npm login
```

### 連続実行タスク

依存関係のあるタスクは個別セルに分割:

```bash {"name":"step1-install"}
npm install
```

```bash {"name":"step2-build"}
npm run build
```

```bash {"name":"step3-test"}
npm test
```

## アンチパターン

### 避けるべきこと

1. **長すぎるコマンド**: 複数行に分割するか、スクリプトファイルに切り出す
2. **ハードコードされたパス**: 相対パスや環境変数を使用
3. **名前なしセル**: 再利用性のため`name`を付与
4. **すべてを実行可能に**: 説明用のコードブロックは言語タグのみ（設定なし）
