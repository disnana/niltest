# 動作モード

niltest は環境変数または `niltest.configure()` の設定によって  
コードを1行も書き換えずに3つのモードで動作します。

---

## モード一覧

| モード | 設定 | 用途 |
|---|---|---|
| **本番運用モード** | `PRODUCTION=true` | 本番環境へのデプロイ時 |
| **モックモード** | `MODE=MOCK` | DB・外部 API なしの開発・手動動作確認 |
| **テストモード** | `MODE=TEST` (`niltest.run_tests()`) | 自動テストの実行 |

---

## ❶ 本番運用モード（`PRODUCTION=true`）

```bash
PRODUCTION=true python app.py
```

または

```python
import niltest
niltest.configure(production=True)
```

### 挙動

| 対象 | 挙動 |
|---|---|
| `@scenario` デコレータ | 元の関数をそのまま返す（ラッパーなし） |
| `if expect:` ブロック | `expect` が `False` となりブロックごとスキップ |
| `expect.case(...)` | 呼び出し自体が発生しない |
| 実際の実装コード | **そのまま実行される** |

### パフォーマンス

デコレータのラッパーは生成されません。`if expect:` の真偽判定コストは残るため、性能要件が厳しい場合は `benchmark_production.py` を対象環境で実行してください。

---

## ❷ モックモード（`MODE=MOCK`）

```bash
MODE=MOCK python app.py
```

または

```python
niltest.configure(production=False, mode="MOCK")
```

### 挙動

関数が呼び出されると `expect.case` の登録が順に実行されます。  
`given` が実際に渡された引数と**完全一致**した時点で即座に `returns` を返却し、  
以降の `expect.case` および実際の実装コードは**実行されません**。

```
呼び出し: process_payment(amount=5_000, user_status="member")
  ↓
expect.case("異常系: ...", given=dict(amount=-1, ...), ...)  ← 不一致、スキップ
expect.case("正常系: プレミアム...", given=dict(..., user_status="premium"), ...)  ← 不一致、スキップ
expect.case("正常系: 通常決済", given=dict(amount=5_000, user_status="member"), returns="approved")
  ↓ 一致！
即座に "approved" を返却。実装コードは実行されない。
```

### ユースケース

- DB・外部 API が使えない環境での開発・動作確認
- フロントエンドやクライアントのテスト用スタブサーバー
- CI 環境でのインテグレーションテストの一部をスキップ

---

## ❸ テストモード（`niltest.run_tests()`）

```python
niltest.configure(mode="TEST")
niltest.run_tests()          # 全 @scenario 関数を対象
niltest.run_tests(my_func)   # 特定の関数だけ対象
```

### 挙動

各 `expect.case` の `given` を kwargs として関数を**実際に呼び出し**、  
返ってきた値が `returns` と一致するかを自動検証します。

```
[niltest] Scenario: 決済処理のビジネスロジック仕様
--------------------------------------------------
  [PASS] 異常系: 無効な決済金額
  [PASS] 正常系: プレミアムユーザー
  [PASS] 正常系: 高額決済は審査待ち
  [FAIL] 正常系: 通常決済は自動承認
         given  : {'amount': 5000, 'user_status': 'member'}
         returns: 'approved'
         actual : 'under_review'

  結果: 3 passed / 1 failed
```

### pytest との違い

| 比較項目 | pytest | niltest |
|---|---|---|
| テストコードの場所 | `tests/` 以下の別ファイル | 関数の先頭（実装と同じ場所） |
| モック定義の場所 | `conftest.py` や `unittest.mock` | 同じ `expect.case` を共用 |
| 仕様の把握 | テストコードを開く必要がある | 関数を開くだけで一目でわかる |
| 本番への影響 | バリデータを挟むと遅くなる | ラッパーなし。`if expect:` の真偽判定のみ |

niltest は pytest の**代替**ではありません。  
pytest と組み合わせて使うことも可能です。  
niltest のテストランナーは「仕様ケースの動作確認」に特化しています。
