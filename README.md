# niltest
[![PyPI version](https://img.shields.io/pypi/v/niltest.svg)](https://pypi.org/project/niltest/)
[![Python versions](https://img.shields.io/pypi/pyversions/niltest.svg)](https://pypi.org/project/niltest/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://static.pepy.tech/badge/niltest)](https://pepy.tech/project/niltest)
[![Tests](https://github.com/disnana/niltest/actions/workflows/ci.yml/badge.svg)](https://github.com/disnana/niltest/actions/workflows/ci.yml)

> Executable specifications, mocks, and lightweight tests—next to the Python function they describe.

[日本語](#日本語) · [English](#english) · [Documentation](https://niltest.disnana.com/docs/) · [MIT License](./LICENSE)

## 日本語

通常、仕様・モック・テストは別々のファイルに散らばります。niltest は、関数先頭の `if expect:` ブロックに実行可能な仕様例をまとめます。同じケースがエディタ上の説明、開発用モック、実装チェックの3つに使われます。

```python
import niltest
from niltest import expect, scenario

niltest.configure(mode="mock")  # @scenarioより前に指定

@scenario("割引計算")
def price(total: int, member: bool = False) -> int:
    if expect:
        expect.case(
            "会員は10%引き",
            given={"total": 1_000, "member": True},
            returns=900,
        )
    return int(total * 0.9) if member else total

assert price(1_000, member=True) == 900

niltest.configure(mode="test")
result = niltest.run_tests(price)
assert result.success
```

### 3分で試す

Python 3.10以降のWindows、macOS、Linuxに対応しています。

```bash
git clone https://github.com/disnana/niltest.git
cd niltest
python -m venv .venv
```

仮想環境を有効化します。

```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate
```

インストールしてデモを実行します。仮想環境を有効化済みなら、通常は次のコマンドを全OSで利用できます。

```bash
pip install -e ".[dev]"
niltest run examples.demo --language ja
python -m pytest
```

Pythonを明示する場合、Windowsでは `python -m pip install -e ".[dev]"`、Ubuntu・macOSでは `python3 -m pip install -e ".[dev]"` を使用してください。環境によっては `pip3 install` も利用できます。

### 何が新しいか

- 仕様を実装のすぐ隣で読める
- 固定値、型、dataclass、Pydantic、バリデータ関数を同じAPIで検証
- 同期・非同期関数に対応
- CLIの終了コードとJSON結果をCIから利用可能
- OS言語を自動検出し、日本語・英語を標準搭載
- `register_locale()` と翻訳テンプレートで言語を拡張可能
- 未指定では安全な `production` モード。`NILTEST_MODE=mock` または `test` を明示して開発機能を有効化

> niltest は pytest の代替ではありません。小さな実行可能仕様をコードの近くに置き、pytestやCIを補完するツールです。

### 型付き仕様とPydantic（v1.1）

`conforms_to()` はPydanticの `TypeAdapter` を使い、戻り値を任意の型注釈に照合します。
`BaseModel`、`list[User]`、Union、`Annotated` の制約に対応します。仕様ケースを実行すると、
`given` の辞書は関数の型注釈に従って検証され、Pydanticモデルなどへ正規化されてから関数へ渡されます。
通常の関数呼び出しやproductionモードの入力には介入しません。

```bash
pip install "niltest[pydantic]"
```

```python
from pydantic import BaseModel
from niltest import case, conforms_to, docs, scenario

class User(BaseModel):
    id: int
    name: str

@scenario("ユーザー取得")
@docs(case("存在する", given={"user_id": 1}, returns=conforms_to(User)))
def fetch_user(user_id: int) -> dict[str, object]:
    return {"id": user_id, "name": "Alice"}
```

大きなモジュールでは、関数シグネチャ、入出力型、ケース、モック可能性、入力エラーを一覧できます。

```bash
niltest inspect your_package.services --language ja
niltest inspect your_package.services --json
```

### 呼び出し時コストをゼロにする宣言型API

既存の `if expect:` はそのまま使えます。関数内の条件分岐も残したくない場合は、ケースを `@docs` で囲みます。

```python
from niltest import case, docs, scenario

@scenario("配送料")
@docs(case("プレミアム会員", given={"premium": True}, returns=0))
def shipping_fee(premium: bool) -> int:
    return 0 if premium else 500
```

既定の `NILTEST_MODE=production` では `@scenario` が元関数をそのまま返します。関数の呼び出し時にniltestのラッパーも条件分岐もありません。`mock` と `test` は、対象モジュールをimportする前に明示してください。

本番経路を実測する場合は、プレーン関数・従来の `if expect:` API・宣言型 `@docs` APIを比較する同梱ベンチマークを実行できます。

```bash
python benchmark_production.py
```

## English

Tests, mock definitions, and documentation often drift across separate files. niltest turns examples declared at the top of a function into all three: readable specifications, fixed development mocks, and executable implementation checks.

### Quick start

The project supports Python 3.10+ on Windows, macOS, and Linux. Follow the setup commands above, then run:

```bash
niltest run examples.demo --language en
niltest run examples.demo --json
```

The command exits with `0` when every case passes, `1` for specification failures, and `2` for usage or import errors.

See the [English documentation](https://niltest.disnana.com/docs/en/), [API reference](https://niltest.disnana.com/docs/en/api/), and [localization guide](https://niltest.disnana.com/docs/en/localization/).

## Built with Codex and GPT-5.6

Codex and GPT-5.6 were used as an engineering partner across the core implementation: repository audit, API design, async defect diagnosis, localization architecture, CLI/result modeling, tests, packaging, and bilingual documentation. Important decisions remained reviewable in the working session and were validated against executable tests rather than accepted as generated text.

This workflow compressed a sequence that normally requires separate architecture, implementation, QA, packaging, and documentation passes into one continuous loop: inspect → propose → patch → run tests → inspect failures → refine.

## License

MIT © 2026 Disnana
