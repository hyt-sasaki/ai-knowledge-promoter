# tech spike実装ガイド

このガイドは、[tech-spike-template.md](../templates/tech-spike-template.md) を使用して技術検証結果を記録する際の詳細な実装ガイドです。

## 技術検証の目的

design.md作成前に最小限の実験コードで技術的妥当性を検証し、設計精度を向上させます。

## いつ実行するか

以下のいずれかに該当する場合、技術検証を実行します：

✅ 複数の技術選択肢がある（例: ライブラリA vs B、アーキテクチャパターンX vs Y）
✅ 新しいライブラリ・技術の学習コストが高い
✅ パフォーマンス・互換性の懸念がある
✅ 設計判断に実験的検証が必要
✅ 既存システムとの統合リスクがある

## いつスキップするか

❌ 技術スタックが確定している
❌ 既知のパターンで実装可能
❌ 単純なCRUD操作のみ
❌ リスクが低く、後戻りコストが小さい

## Context7活用パターン

技術検証の前に、Context7で最新のライブラリ情報を調査します。

### 基本フロー

1. **ライブラリIDを解決**
   - MCPツール: `mcp__plugin_context7_context7__resolve-library-id`
   - パラメータ:
     - `libraryName`: 調査したいライブラリ名（例: "Next.js"）
     - `query`: 質問内容（例: "React Server Componentsのデータフェッチパターン"）

2. **ドキュメント検索**
   - MCPツール: `mcp__plugin_context7_context7__query-docs`
   - パラメータ:
     - `libraryId`: Step 1で取得したID（例: "/vercel/next.js"）
     - `query`: 具体的な質問（例: "Server Components data fetching patterns"）

### 実例：React Server Components vs Client Components

**調査項目**: Next.js App RouterでのServer Components vs Client Components選択

**Context7調査手順**:

1. ライブラリIDを解決
   - libraryName: "Next.js"
   - query: "Server ComponentsとClient Componentsのデータフェッチパターンを比較したい"
   - 結果: `/vercel/next.js`

2. Server Componentsパターン調査
   - libraryId: `/vercel/next.js`
   - query: "Server Components data fetching patterns and performance benefits"
   - 結果メモ:
     - fetch()が自動的にデデュープされる
     - ゼロクライアントサイドJavaScript
     - SEOに優れる

3. Client Componentsパターン調査
   - libraryId: `/vercel/next.js`
   - query: "Client Components hydration performance and use cases"
   - 結果メモ:
     - インタラクティブ性が必要な場合に使用
     - useState, useEffectが使える
     - ハイドレーションのオーバーヘッドあり

### 実例：FastAPI認証ライブラリ比較

**調査項目**: FastAPIでの認証ライブラリ選択（FastAPI-Users vs Authlib vs 自前実装）

**Context7調査手順**:

1. FastAPI-Users調査
   - libraryName: "FastAPI-Users"
   - query: "FastAPI-Usersの認証パターンとセキュリティベストプラクティス"
   - 結果メモ:
     - すぐに使えるユーザー管理機能
     - OAuth2対応
     - ドキュメント豊富

2. Authlib調査
   - libraryName: "Authlib"
   - query: "Authlib FastAPI integration patterns"
   - 結果メモ:
     - 柔軟性が高い
     - OAuth2/OpenID Connectサポート
     - 学習コストやや高め

3. FastAPI公式ドキュメント調査
   - libraryId: `/tiangolo/fastapi`
   - query: "authentication security best practices"
   - 結果メモ:
     - JWT推奨パターン
     - セキュリティヘッダーの設定例

## 最小実験コードの作成

Context7調査の後、実験コードで検証します。

### 実験ディレクトリ構成

```bash
# 実験コード用ディレクトリ作成
mkdir -p openspec/changes/<change-id>/spike/

# 構成例
openspec/changes/<change-id>/spike/
├── results.md           # 検証結果レポート
├── experiment-a.py      # アプローチA（例: FastAPI-Users）
├── experiment-b.py      # アプローチB（例: Authlib）
└── benchmark.py         # パフォーマンス比較（必要な場合）
```

### 実験コードの原則

✅ **最小限**: 検証に必要な機能のみ実装
✅ **使い捨て**: 本番コードに含めない（spike/配下に隔離）
✅ **比較可能**: 複数のアプローチを同じ条件で比較
✅ **計測可能**: パフォーマンス、学習コスト、保守性を定量化

### 実験コード例：FastAPI-Users vs Authlib

**experiment-a.py（FastAPI-Users）**
```python
# FastAPI-Users を使った最小限の認証実装
from fastapi import FastAPI
from fastapi_users import FastAPIUsers

app = FastAPI()

# セットアップコードを最小限に記述
# 目的: すぐに使えるか？設定は直感的か？

# 計測: セットアップ時間、コード行数、理解度（主観）
```

**experiment-b.py（Authlib）**
```python
# Authlib を使った最小限の認証実装
from fastapi import FastAPI
from authlib.integrations.starlette_client import OAuth

app = FastAPI()

# セットアップコードを最小限に記述
# 目的: 柔軟性は？複雑さは？

# 計測: セットアップ時間、コード行数、理解度（主観）
```

**benchmark.py（パフォーマンス比較）**
```python
import time
import requests

# 簡易的なパフォーマンステスト
# 例: ログインエンドポイントのレスポンスタイム計測

def benchmark_approach_a():
    start = time.time()
    # experiment-a.pyのエンドポイントを呼び出し
    requests.post("http://localhost:8000/auth/login", ...)
    return time.time() - start

def benchmark_approach_b():
    # 同様にexperiment-b.pyを計測
    pass

# 結果を比較
```

## 検証結果の記録

`openspec/changes/<change-id>/spike/results.md` に結果を記録します。

### 記録例

```markdown
# 技術検証結果

## 検証項目
FastAPIでの認証ライブラリ選択

## Context7調査サマリー
- FastAPI-Users: すぐ使える、ドキュメント豊富、柔軟性やや低い
- Authlib: 柔軟性高い、学習コストやや高い、カスタマイズ容易

## 実験1: FastAPI-Users
- **コード**: spike/experiment-a.py
- **セットアップ時間**: 30分
- **コード行数**: 50行
- **パフォーマンス**: ログイン 100ms（100リクエスト平均）
- **所感**: セットアップが簡単。ドキュメント通りで動作。カスタマイズ余地少ない。

## 実験2: Authlib
- **コード**: spike/experiment-b.py
- **セットアップ時間**: 90分
- **コード行数**: 120行
- **パフォーマンス**: ログイン 95ms（100リクエスト平均）
- **所感**: 柔軟だがセットアップ複雑。ドキュメントが散在。

## 定量比較

| 項目 | FastAPI-Users | Authlib |
|------|---------------| --------|
| セットアップ時間 | 30分 | 90分 |
| コード行数 | 50行 | 120行 |
| パフォーマンス | 100ms | 95ms |
| 学習曲線 | 緩やか | 急峻 |
| カスタマイズ性 | 低 | 高 |

## 推奨
**FastAPI-Usersを採用**

理由：
- パフォーマンス差は5ms（許容範囲内）
- セットアップ時間が3倍速い
- チームの学習コストを最小化
- 当面の要件（基本的なユーザー認証）には十分

将来的にカスタマイズ要件が増えた場合、Authlibへの移行を検討。
```

## 定量データ収集のベストプラクティス

### セットアップ時間の計測

実験開始から最初の動作確認までの時間を計測：

```bash
# タイマー開始
START=$(date +%s)

# 実験コード作成・実行
# ...

# タイマー終了
END=$(date +%s)
echo "Setup time: $((END - START)) seconds"
```

### コード行数の計測

```bash
# Pythonの場合
wc -l spike/experiment-a.py

# Node.jsの場合
wc -l spike/experiment-a.js

# 複数ファイル合計
find spike/ -name "*.py" | xargs wc -l
```

### パフォーマンスの計測

```bash
# cURLでレスポンスタイム計測
time curl -X POST http://localhost:8000/api/endpoint

# Apache Benchで複数リクエスト計測
ab -n 100 -c 10 http://localhost:8000/api/endpoint

# Pythonで詳細計測
python -m cProfile spike/experiment-a.py
```

## 推奨判断基準

採用アプローチを選択する際の判断基準：

### 1. セットアップ時間の重み

- **小規模プロジェクト（1-2人）**: セットアップ時間を重視（50%）
- **中規模プロジェクト（3-10人）**: 学習コストとドキュメント品質を重視（40%）
- **大規模プロジェクト（10人以上）**: 保守性とカスタマイズ性を重視（40%）

### 2. パフォーマンス差の許容範囲

- **10ms以下**: 無視可能
- **10-100ms**: 許容範囲（他の要素を優先）
- **100ms以上**: 重要（パフォーマンス優先の場合）

### 3. 学習曲線の評価

- **緩やか**: チーム全員が1日以内に理解可能
- **普通**: 2-3日で基本的な使用法を習得可能
- **急峻**: 1週間以上の学習が必要

## カスタマイズのヒント

### 1. 複数言語での実験

Pythonだけでなく、Node.js、Go、Rust等で実験可能：

```bash
# Node.js
spike/experiment-a.js
spike/experiment-b.ts

# Go
spike/experiment-a.go
spike/experiment-b.go

# Rust
spike/experiment-a.rs
spike/experiment-b.rs
```

### 2. スクリーンショットの活用

実験結果の視覚的な証拠を保存：

```bash
spike/screenshots/
├── experiment-a-result.png
├── experiment-b-result.png
└── performance-comparison.png
```

### 3. 依存関係の記録

実験で使用した依存関係を記録：

```bash
# Python
spike/requirements.txt

# Node.js
spike/package.json

# Go
spike/go.mod

# Rust
spike/Cargo.toml
```

### 4. ベンチマーク自動化

定期的にベンチマークを実行し、結果を比較：

```python
# spike/benchmark.py
import json
import time

results = {
    "approach_a": benchmark_approach_a(),
    "approach_b": benchmark_approach_b(),
    "timestamp": time.time()
}

with open("spike/benchmark-results.json", "w") as f:
    json.dump(results, f, indent=2)
```

## よくある質問

**Q: 実験コードはどこまで作り込むべきか？**

A: 検証に必要な最小限のみ。本番コードの品質は不要です。目安は1-2時間で完成するレベル。

**Q: パフォーマンステストは必須か？**

A: パフォーマンスが要件に含まれる場合のみ。基本的な機能検証なら不要です。

**Q: 実験コードは本番に含めるか？**

A: 含めません。spike/配下に隔離し、後で削除またはアーカイブします。

**Q: Context7で情報が見つからない場合は？**

A: 公式ドキュメント、GitHub、技術ブログを直接参照します。Context7はあくまで補助ツールです。

**Q: 複数のアプローチを試す順番は？**

A: 最も有望なアプローチから順に試します。明らかに劣る選択肢は実験をスキップしても構いません。

**Q: 実験結果が予想と異なる場合は？**

A: 追加の実験を行うか、Context7で追加調査します。必要に応じてdesign.mdで判断を再検討します。

**Q: 実験コードのコミット戦略は？**

A: git worktreeを使用し、実験用ブランチで頻繁にコミットし、最終的にfeatureブランチに--squashマージします。詳細は [step0.5-tech-spike.md](step0.5-tech-spike.md#コミット戦略git-worktree活用パターン) を参照。

## 次のステップ

spike/results.md完成後：

### design.md作成が必要な場合
→ **Step 0.9: Design** へ進む

spike/results.mdの推奨アプローチをdesign.mdに反映します。

### design.md不要な場合
→ **Step 1: Runbook & Red** へ進む

spike/results.mdの推奨アプローチで直接実装を開始します。
