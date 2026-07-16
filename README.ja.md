# niltest

[![PyPI version](https://img.shields.io/pypi/v/niltest.svg)](https://pypi.org/project/niltest/)
[![Python versions](https://img.shields.io/pypi/pyversions/niltest.svg)](https://pypi.org/project/niltest/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)
[![Tests](https://github.com/disnana/niltest/actions/workflows/ci.yml/badge.svg)](https://github.com/disnana/niltest/actions/workflows/ci.yml)

> Python関数のすぐ隣に置く、実行可能な仕様・開発用モック・軽量チェック。

[English README](./README.md) · [ドキュメント](https://niltest.disnana.com/docs/) · [PyPI](https://pypi.org/project/niltest/) · [ライセンス](./LICENSE)

niltestは代表的な振る舞いを実装のすぐ隣へ置きます。ひとつのケースを、読める仕様、開発中の固定モック、本物の実装チェックとして再利用できます。Windows、macOS、LinuxのPython 3.10以降に対応しています。

## インストール

```bash
# 仮想環境を有効化済みの場合
pip install niltest

# Windows
python -m pip install niltest

# Ubuntu / macOS
python3 -m pip install niltest
```

## 完全な例

```python
import niltest
from niltest import Mode, expect, scenario

niltest.configure(mode=Mode.MOCK)  # デコレータ付きモジュールのimport前に指定

@scenario("配送料")
def shipping_fee(subtotal: int, premium: bool = False) -> int:
    if expect:
        expect.case(
            "プレミアム会員は無料",
            given={"subtotal": 1_000, "premium": True},
            returns=0,
        )
    return 0 if premium or subtotal >= 5_000 else 500

assert shipping_fee(1_000, premium=True) == 0

niltest.configure(mode=Mode.TEST)
assert niltest.run_tests(shipping_fee).success
```

## モードとセットアップ

安全な既定値は`production`です。このモードではniltestのラッパーを作らず、元の関数を返します。`test`は本物の実装に対してケースを実行し、`mock`は一致したケースの固定値を返します。

```python
from niltest import Mode, configure

configure(mode=Mode.TEST)   # 推奨: 補完と型チェックが効く
configure(mode="test")      # 互換性と簡潔さのために利用可能
```

開発モードは、`@scenario`を含むモジュールをimportする前に指定します。Python起動前なら`NILTEST_MODE=test`または`NILTEST_MODE=mock`も使えます。

## 期待値と型付き入力

`returns`には通常の値、dataclass、型、Pydanticを使う`conforms_to()`、バリデータ関数を渡せます。`niltest[pydantic]`をインストールすると、Pydanticでケース入力を検証・正規化できます。

```python
from niltest import case, docs, scenario

@scenario("出金")
@docs(case("残高不足", given={"balance": 100, "amount": 150}, raises=ValueError, match="insufficient"))
def withdraw(balance: int, amount: int) -> int:
    if amount > balance:
        raise ValueError("insufficient funds")
    return balance - amount
```

`returns`と`raises`は必ずどちらか一方だけを指定します。例外ケースは本物の実装を検証し、モックには使われません。

## 仕様をinspectする

`inspect`はモジュールをimportして登録済みシナリオを一覧します。ケースは実行しません。`your_package.services`には、`your_package/services.py`のようなimport可能なモジュールパスを指定します。

```bash
niltest inspect your_package.services                 # 端末で読む
niltest inspect your_package.services --format json   # CI・ツール連携
niltest inspect your_package.services --format markdown # レビュー資料
```

リポジトリには[実行対象のサンプル](./examples/08_inspect_report.py)、[英語のMarkdown結果](./examples/08_inspect_report.result.md)、[日本語の読み方付き結果](./examples/08_inspect_report.result.ja.md)を同梱しています。`--json`は`--format json`の互換エイリアスです。

## pytestとCI

niltestはpytestの代替ではなく補完です。`--niltest`を付けると、各宣言ケースを独立したpytest itemとして収集し、通常のレポート、JUnit XML、coverageへ統合します。フラグなしではプラグインは何もしません。

```bash
pytest --niltest --niltest-module=your_package.specs
pytest --niltest --junitxml=report.xml --cov=your_package
```

```toml
[tool.pytest.ini_options]
niltest_modules = ["your_package.specs"]
```

## 本番で呼び出し時コストをなくす

関数外に仕様を宣言したい場合は`@docs`を使います。productionモードでは`@scenario`が元の関数を返すため、実行時のラッパーもniltest由来の分岐もありません。

```python
from niltest import case, docs, scenario

@scenario("配送料")
@docs(case("プレミアム会員", given={"premium": True}, returns=0))
def shipping_fee(premium: bool) -> int:
    return 0 if premium else 500
```

## 多言語化

日本語と英語を標準搭載しています。niltestはOSの言語設定を検出し、判別できない場合は英語へフォールバックします。`register_locale()`と検証付きテンプレートで言語を追加できます。

## リリースの来歴証明

PyPI配布物はTrusted PublishingとSigstore attestationを利用します。GitHub Releaseにはビルド来歴が付き、すべての配布物にはSLSA Build Level 3 provenanceがあります。

```bash
gh attestation verify niltest-*.whl --repo disnana/niltest
gh attestation verify niltest-*.tar.gz --repo disnana/niltest
```

## CodexとGPT-5.6の活用

CodexとGPT-5.6は、リポジトリ監査、API設計、実装、テスト失敗の診断、パッケージ化、多言語化、ドキュメント整備を支援しました。変更は実行可能なテストとCIで検証しています。

## ライセンス

MIT © 2026 Disnana
