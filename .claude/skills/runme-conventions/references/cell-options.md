# セルレベル設定オプション一覧

## 目次

- [実行制御](#実行制御)
- [ディレクトリ・環境](#ディレクトリ環境)
- [インタラクション](#インタラクション)
- [出力・表示](#出力表示)
- [構文形式](#構文形式)

## 実行制御

### background

バックグラウンドプロセスとして実行。

| 項目 | 値 |
|------|-----|
| デフォルト | `false` |
| 用途 | 長時間実行プロセス、サーバー起動 |

```bash {"background":"true","name":"dev-server"}
npm run dev
```

### excludeFromRunAll

`runme run --all`操作から除外。

| 項目 | 値 |
|------|-----|
| デフォルト | `false` |
| 用途 | 危険なコマンド、オプショナルなタスク |

```bash {"excludeFromRunAll":"true","name":"cleanup"}
rm -rf node_modules
```

### skipPrompts

インタラクティブプロンプトをバイパス。

| 項目 | 値 |
|------|-----|
| デフォルト | `false` |
| 用途 | CI/CD環境、自動化スクリプト |

## ディレクトリ・環境

### cwd

セル実行時の作業ディレクトリを変更。**マークダウンファイルからの相対パス**で指定。

| 項目 | 値 |
|------|-----|
| デフォルト | 空白（マークダウンファイルと同じディレクトリ） |
| 用途 | サブディレクトリでのコマンド実行 |

```bash {"cwd":"../mcp-server","name":"build"}
npm run build
```

### promptEnv

環境変数の入力を促すかどうか。

| 項目 | 値 |
|------|-----|
| デフォルト | `auto` |
| 値 | `auto`, `yes`, `no` |
| 用途 | 環境変数が必要なコマンド |

## インタラクション

### interactive

ユーザー入力を許可するか。

| 項目 | 値 |
|------|-----|
| デフォルト | `false` |
| 用途 | パスワード入力、確認プロンプト |

```bash {"interactive":"true","name":"login"}
npm login
```

### interpreter

シェバング行で使用するプログラム。

| 項目 | 値 |
|------|-----|
| デフォルト | 言語IDから自動推測 |
| 用途 | 特定のシェル/インタープリタを指定 |

```bash {"interpreter":"zsh"}
source ~/.zshrc && echo $SHELL
```

## 出力・表示

### closeTerminalOnSuccess

成功時にターミナルを非表示。

| 項目 | 値 |
|------|-----|
| デフォルト | `true` |
| 用途 | 結果を確認したい場合は`false` |

### mimeType

出力の媒体タイプを指定。

| 項目 | 値 |
|------|-----|
| デフォルト | 空白（自動検出） |
| 用途 | 特定の出力形式を強制 |

### terminalRows

ターミナル表示行数。

| 項目 | 値 |
|------|-----|
| デフォルト | 自動設定 |
| 用途 | 出力表示領域の調整 |

### name

セルの識別名。`runme run <name>`で実行可能。

| 項目 | 値 |
|------|-----|
| デフォルト | 自動生成 |
| 用途 | CLI実行、タスク識別 |

```bash {"name":"test"}
npm test
```

## 構文形式

### JSON形式（推奨）

```bash {"name":"deploy","cwd":"../app","excludeFromRunAll":"true"}
npm run deploy
```

### 複数オプション

```bash {"background":"true","interactive":"false","name":"watch"}
npm run watch
```

### 注意事項

- オプション値は文字列で指定（`"true"`、`"false"`）
- `runme fmt`でフォーマットを正規化
- VSCode拡張機能と互換性を保つためJSON形式を使用
