# niltest

**Executable specifications, fixed development mocks, and lightweight checks—next to the Python function they describe.**

[日本語](#日本語) · [Documentation](https://niltest.disnana.com/docs/) · [GitHub](https://github.com/disnana/niltest/) · [Issues](https://github.com/disnana/niltest/issues)

niltest lets one `expect.case()` definition serve three purposes:

- readable behavior close to the implementation;
- a fixed mock when databases or external APIs are unavailable;
- an executable check against the real function.

It has no runtime dependencies and supports Python 3.10+ on Windows, macOS, and Linux.

## Install

```bash
# Active virtual environment (Windows, macOS, or Linux)
pip install niltest

# Windows
python -m pip install niltest

# Ubuntu / macOS
python3 -m pip install niltest
```

## A complete example

```python
import niltest
from niltest import expect, scenario


@scenario("Shipping fee")
def shipping_fee(subtotal: int, premium: bool = False) -> int:
    if expect:
        expect.case(
            "Premium members ship free",
            given={"subtotal": 1_000, "premium": True},
            returns=0,
        )
        expect.case(
            "Standard shipping",
            given={"subtotal": 1_000, "premium": False},
            returns=500,
        )

    return 0 if premium or subtotal >= 5_000 else 500


niltest.configure(mode="MOCK")
assert shipping_fee(1_000, premium=True) == 0

niltest.configure(mode="TEST")
result = niltest.run_tests(shipping_fee)
assert result.success
```

## CLI and CI

```bash
niltest run your_package.specs --language en
niltest run your_package.specs --json
```

The CLI exits with `0` when all cases pass, `1` for specification failures, and `2` for usage or import errors. JSON output and the structured `RunResult` API make niltest easy to compose with CI and other developer tools.

## Expectations

`returns` supports:

- plain values and collections;
- dataclass instances;
- Pydantic models;
- type-only checks such as `returns=UserData`;
- custom validators such as `returns=lambda result: result["count"] > 0`;
- synchronous and asynchronous functions.

## Production path

Set `PRODUCTION=true` before importing decorated modules. In this mode, `@scenario` returns the original function without creating a wrapper. The explicit `if expect:` truth check remains; niltest documents this measurable cost instead of claiming absolute zero overhead.

For zero niltest cost at function-call time, use the declaration-style API. The existing inline API remains fully supported.

```python
from niltest import case, docs, scenario

@scenario("Shipping fee")
@docs(case("Premium", given={"premium": True}, returns=0))
def shipping_fee(premium: bool) -> int:
    return 0 if premium else 500
```

With `PRODUCTION=true`, this returns the original function: no wrapper and no `if expect:` branch in its body.

## Localization

Japanese and English are built in. niltest detects the OS locale, falls back to English, and exposes `register_locale()` plus a validated template for additional languages.

## 日本語

niltestは、Python関数の先頭に代表的な入力と期待値を書くことで、同じ定義を「読める仕様」「開発用モック」「実装チェック」に再利用する軽量ライブラリです。

```bash
python -m pip install niltest
niltest run your_package.specs --language ja
```

日本語の詳しい使い方、モック・非同期関数・バリデータ・本番モード・応用例は[公式ドキュメント](https://niltest.disnana.com/docs/)で確認できます。

MIT © 2026 Disnana
