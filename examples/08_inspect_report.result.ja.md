# niltest 仕様レポート

次のコマンドで確認するための、日本語の読み方付き出力例です。

```bash
niltest inspect examples.08_inspect_report --format markdown
```

## `subscription_quote(plan: str, seats: int, annual: bool = False) -> int`

**シナリオ:** Subscription quote

**戻り値:** `int`

| ケース | 入力 | 期待値 | モック可能 | 有効 | 定義元 |
| --- | --- | --- | --- | --- | --- |
| team annual plan | {'plan': 'team', 'seats': 3, 'annual': True} | 288 | はい | はい | examples/08_inspect_report.py:8 |
| at least one seat | {'plan': 'starter', 'seats': 0, 'annual': False} | raises ValueError matching 'at least one' | いいえ | はい | examples/08_inspect_report.py:14 |

- **モック可能** は、mockモードでそのケースの期待値を固定値として返せるかを示します。例外を期待するケースはモックには使われません。
- 実際の`Source`列は絶対パスになるため、環境ごとに表示が変わります。
