# API リファレンス

---

## `niltest.configure()`

動作モードをコードから明示的に設定します。  
指定しない場合は環境変数から自動ロードされます。

```python
niltest.configure(
    production: bool | None = None,  # True で本番モード（ゼロコスト）
    mode: str | None = None,         # "MOCK" または "TEST"
)
```

### 環境変数による自動設定

| 環境変数 | 説明 |
|---|---|
| `PRODUCTION=true` | 本番モードで起動。すべての検証コードが無効化される |
| `MODE=MOCK` | モックモードで起動 |
| `MODE=TEST` | テストモードで起動 |

### 使用例

```python
import niltest

# コードから明示的に設定
niltest.configure(production=False, mode="MOCK")

# 本番モードへの切り替え
niltest.configure(production=True)
```

> **注意**: `@scenario` デコレータはインポート時に評価されます。  
> `production=True` はモジュールインポート前に環境変数で設定するか、  
> インポート直後 かつ デコレータ定義前に `configure()` を呼び出してください。

---

## `@scenario(title)`

関数を仕様検証可能な対象としてマークするデコレータ。

```python
@scenario(title: str)
def my_func(...) -> ...:
    ...
```

### 引数

| 引数 | 型 | 説明 |
|---|---|---|
| `title` | `str` | このシナリオのタイトル。docstring やテスト結果に表示される |

### 本番環境での挙動

`PRODUCTION=true` の場合、デコレータは元の関数を**そのまま返します**。  
ラッパーは生成されず、呼び出し時のオーバーヘッドはゼロです。

---

## `expect.case()`

仕様ケースを1件登録します。  
`if expect:` ブロックの中で呼び出します。

```python
expect.case(
    name: str,          # ケース名（例: "正常系: 管理者ユーザー"）
    *,
    desc: str = "",     # このケースの説明（任意）
    given: dict,        # 代表的な入力引数（kwargs 形式）
    returns: Any,       # そのときに期待する戻り値
)
```

### 使用例

```python
@scenario("ユーザー取得の仕様")
def get_user(user_id: int, role: str = "member") -> dict:
    if expect:
        expect.case("正常系: 一般ユーザー",
            desc="一般ユーザーIDで呼び出した場合にユーザー情報を返す",
            given=dict(user_id=1, role="member"),
            returns={"id": 1, "name": "Alice"},
        )
        expect.case("異常系: 存在しないID",
            desc="存在しないIDを指定した場合は None を返す",
            given=dict(user_id=9999, role="member"),
            returns=None,
        )

    # 実際の実装
    return fetch_from_db(user_id)
```

### `returns` に渡せる値の種類

`returns` は用途に応じて4種類の値を受け付けます。

#### ① プレーン値（デフォルト）
```python
returns="approved"
returns={"id": 1, "name": "Alice"}
returns=None
```
`actual == returns` で比較します。

#### ② dataclass / Pydantic インスタンス
```python
returns=UserData(id=1, name="Alice", role="admin")     # dataclass
returns=UserResponse(status="ok", code=200)             # Pydantic
```
フィールド単位で比較します（`asdict()` / `model_dump()` を使用）。
モックモードでは、インスタンスがそのまま返却されます。

#### ③ クラス型のみ（isinstance チェック）
```python
returns=UserData    # インスタンスの型が UserData であることだけ確認
```
返される値が毎回変わる（IDがランダムなど）が、**型は確定している** 場合に使います。
モックには使えません（返す値が特定できないため）。

#### ④ callable / lambda（バリデータ）
```python
returns=lambda r: isinstance(r["token"], str) and r["user_id"] == 42
```
UUID・タイムスタンプ・乱数など**不定な値を含む戻り値**を検証したい場合に使います。
`actual` をバリデータに渡して `truthy` かどうかを判定します。
モックには使えません。

| 種類 | モック | テスト照合 | 用途 |
|---|---|---|---|
| プレーン値 | 返却 | `==` | 固定値 |
| dataclass/Pydanticインスタンス | 返却 | フィールド比較 | 構造化データ |
| クラス型 (`UserData`) | 使えない | `isinstance` | 型だけ確認したい |
| callable (`lambda`) | 使えない | バリデータ実行 | ランダム・不定な値 |


---

## `niltest.run_tests()`

`@scenario` 関数に定義された `expect.case` を使って自動テストを実行します。

```python
niltest.run_tests(*funcs)
```

### 引数

| 引数 | 説明 |
|---|---|
| `*funcs` | テスト対象の関数を指定。省略するとすべての `@scenario` 関数を実行 |

### 使用例

```python
# 特定の関数だけテスト
niltest.run_tests(get_user)

# すべての @scenario 関数をテスト
niltest.run_tests()
```

### 出力例

```
[niltest] Scenario: ユーザー取得の仕様
--------------------------------------------------
  [PASS] 正常系: 一般ユーザー
  [PASS] 異常系: 存在しないID

  結果: 2 passed / 0 failed
```

### テストの照合ロジック

各 `expect.case` について `func(**given)` を実行し、  
戻り値が `returns` と `==` で一致するかを確認します。  
一致しない場合は `given`・期待値・実際の値を表示します。
