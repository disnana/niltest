# niltest

本番環境でのパフォーマンス影響ゼロを実現しながら、  
**仕様の可視化・モック・自動テストを関数1つの中に完結させる** Python ライブラリ。

---

## なぜ niltest なのか

通常のテスト手法では、実装・テストコード・モック定義の3箇所にコードが散らばります。

```
my_func.py      ← 実装
tests/test_my_func.py  ← テスト
mocks/my_func_mock.py  ← モック
```

niltest ではこれをすべて**関数の先頭の `if expect:` ブロック1箇所**に集約します。

```python
@scenario("決済処理の仕様")
def process_payment(amount: int, user_status: str) -> str:
    if expect:
        expect.case("正常系: 通常決済",
            desc="一般会員で10万円未満は自動承認",
            given=dict(amount=5_000, user_status="member"),
            returns="approved",
        )
        # ... 他のケースも同様

    # 実際の実装（本番・テストモードで動く）
    if amount <= 0:
        return "invalid_amount"
    ...
```

この1箇所の定義から：
- **エディタ上のドックストリング**として仕様が表示される
- **モックモード**では `given` と一致した引数の場合に `returns` を即返却
- **テスト実行**では `given` を引数に実際のコードを呼び出し `returns` と自動照合

---

## インストール

```bash
# リポジトリをクローンしてローカルで使う場合
pip install -e .
```

---

## クイックスタート

```python
import niltest
from niltest import scenario, expect

# 1. 関数に @scenario を付けて expect.case で仕様を定義する
@scenario("ユーザー取得の仕様")
def get_user(user_id: int, role: str = "member") -> dict:
    if expect:
        expect.case("正常系: 一般ユーザー",
            desc="一般ユーザーIDで呼び出した場合",
            given=dict(user_id=1, role="member"),
            returns={"id": 1, "name": "Alice"},
        )
        expect.case("正常系: 管理者",
            desc="管理者IDで呼び出した場合",
            given=dict(user_id=99, role="admin"),
            returns={"id": 99, "name": "Admin"},
        )

    # 実際の実装（DBアクセスなど）
    return fetch_from_db(user_id)


# 2. モックモードで呼び出す（DBに繋がない）
niltest.configure(mode="MOCK")
result = get_user(1, role="member")  # -> {"id": 1, "name": "Alice"}

# 3. 自動テスト（given を引数に実装を呼び出して returns と照合）
niltest.configure(mode="TEST")
niltest.run_tests(get_user)
```

---

## ドキュメント一覧

| ドキュメント | 内容 |
|---|---|
| [concepts.md](./concepts.md) | ゼロコスト設計の仕組みと技術的な背景 |
| [api.md](./api.md) | APIリファレンス（configure / scenario / expect.case / run_tests） |
| [modes.md](./modes.md) | 3つの動作モード（PRODUCTION / MOCK / TEST）の詳細 |
