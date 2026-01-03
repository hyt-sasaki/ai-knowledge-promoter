# フィーチャーフラグガイド

フィーチャーフラグ（Feature Flag）を使用した段階的リリースのガイドラインです。

## フィーチャーフラグの目的

- **安全なリリース**: 本番環境への影響を最小化
- **段階的展開**: 問題発生時の迅速なロールバック
- **並行開発**: 未完成機能をmainブランチにマージ可能

---

## フィーチャーフラグが必要なケース

以下の場合、フィーチャーフラグでスケルトン実装を制御します：

### 必要

- **既存システムへの機能追加**: 既存のエンドポイント・機能に影響する変更
- **破壊的変更（Breaking Changes）**: APIレスポンス形式の変更、データベーススキーマの大幅変更
- **段階的リリース**: 本番環境で段階的にリリースしたい場合

### 不要

- **完全な新規開発**: 新規プロジェクトの立ち上げ、既存システムに影響しない独立した機能
- **内部ツール・CI/CD**: 開発者のみが使用するツール、本番環境に影響しない変更

### 判断が曖昧な場合

フィーチャーフラグの必要性が不明確な場合は、ユーザーに確認します：

```
フィーチャーフラグの使用について確認させてください：

この変更は以下のいずれかに該当しますか？
- 既存システムへの機能追加
- 破壊的変更（Breaking Changes）
- 段階的リリースが必要

該当する場合、フィーチャーフラグで制御することを推奨します。
該当しない場合（完全新規開発等）、フィーチャーフラグは不要です。

フィーチャーフラグを使用しますか？ (Yes/No)
```

---

## 実装パターン

### 環境変数での制御

```python
import os

FEATURE_USER_AUTH_ENABLED = os.getenv("FEATURE_USER_AUTH_ENABLED", "false") == "true"

@app.post("/api/users")
def create_user(user: UserCreate):
    if not FEATURE_USER_AUTH_ENABLED:
        raise HTTPException(status_code=503, detail="Feature not available")

    # 実装
    return {...}
```

### .envファイル

```bash
# 開発環境では有効化
FEATURE_USER_AUTH_ENABLED=true

# 本番環境ではデフォルトでfalse（環境変数未設定）
```

---

## 動作確認

### OFF状態のテスト

```bash
# フィーチャーフラグをOFFに
export FEATURE_<NAME>_ENABLED=false

# APIにアクセス
curl -X POST http://localhost:3000/api/users ...

# 期待: 503 Service Unavailable "Feature not available"
```

### ON状態のテスト

```bash
# フィーチャーフラグをONに
export FEATURE_<NAME>_ENABLED=true

# APIにアクセス
curl -X POST http://localhost:3000/api/users ...

# 期待: 正常なレスポンス（実装された機能が動作）
```

---

## ライフサイクル

### Step 3（スケルトン）

1. フィーチャーフラグが必要か判断
2. 必要な場合、環境変数で制御するコードを実装
3. フラグOFFでmainにマージ

### Step 5（リリース）

1. 全テストが通過していることを確認
2. フラグのON/OFF動作を確認
3. フラグをONにして本番デプロイ
4. 安定後、フラグを削除（オプション）

---

## 関連ステップ

- [Step 3: Skeleton Green](../workflows/step3-skeleton-green.md) - スケルトン実装時の判断
- [Step 5: Archive & Release](../workflows/step5-archive-release.md) - リリース時の有効化
