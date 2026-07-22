# niltest

[![PyPI version](https://img.shields.io/pypi/v/niltest.svg)](https://pypi.org/project/niltest/)
[![Python versions](https://img.shields.io/pypi/pyversions/niltest.svg)](https://pypi.org/project/niltest/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)
[![Tests](https://github.com/disnana/niltest/actions/workflows/ci.yml/badge.svg)](https://github.com/disnana/niltest/actions/workflows/ci.yml)

> Executable specifications, fixed development mocks, and lightweight checks—next to the Python function they describe.

[日本語 README](./README.ja.md) · [Documentation](https://niltest.disnana.com/docs/en/) · [PyPI](https://pypi.org/project/niltest/) · [License](./LICENSE)
<!-- AI integration context: https://niltest.disnana.com/docs/ai-context.json -->

niltest keeps representative behavior beside the implementation. One case can serve as readable documentation, a fixed mock in development, and a check against the real implementation. It supports Python 3.10+ on Windows, macOS, and Linux.

## Install

```bash
# Active virtual environment
pip install niltest

# Windows
python -m pip install niltest

# Ubuntu / macOS
python3 -m pip install niltest
```

## A complete example

```python
import niltest
from niltest import Mode, expect, scenario

niltest.configure(mode=Mode.MOCK)  # Set this before importing decorated modules.

@scenario("Shipping fee")
def shipping_fee(subtotal: int, premium: bool = False) -> int:
    if expect:
        expect.case(
            "Premium members ship free",
            given={"subtotal": 1_000, "premium": True},
            returns=0,
        )
    return 0 if premium or subtotal >= 5_000 else 500

assert shipping_fee(1_000, premium=True) == 0

niltest.configure(mode=Mode.TEST)
assert niltest.run_tests(shipping_fee).success
```

## Modes and setup

`production` is the safe default. It returns the original function without a niltest wrapper. Choose `test` to run cases against the implementation, or `mock` to return fixed values for matching cases.

```python
from niltest import Mode, configure

configure(mode=Mode.TEST)   # Recommended: completion and type checking
configure(mode="test")      # Supported for compatibility and brevity
```

Set a development mode before importing the module that contains `@scenario`. You can also set `NILTEST_MODE=test` or `NILTEST_MODE=mock` before starting Python.

## Expectations and typed inputs

`returns` accepts plain values, dataclass instances, types, Pydantic-backed `conforms_to()` expectations, and validator functions. Install `niltest[pydantic]` to validate and normalize typed case inputs with Pydantic.

```python
from niltest import case, docs, scenario

@scenario("Withdraw funds")
@docs(case("insufficient funds", given={"balance": 100, "amount": 150}, raises=ValueError, match="insufficient"))
def withdraw(balance: int, amount: int) -> int:
    if amount > balance:
        raise ValueError("insufficient funds")
    return balance - amount
```

Use exactly one of `returns` or `raises`. Exception cases verify the real implementation and never act as mocks.

## Inspect specifications

`inspect` imports a module and lists its registered scenarios; it does not execute cases. Replace `your_package.services` with an importable module path such as `your_package/services.py`.

```bash
niltest inspect your_package.services                 # terminal text
niltest inspect your_package.services --format json   # CI and tools
niltest inspect your_package.services --format markdown # review documents
```

The repository includes an [inspectable example](./examples/08_inspect_report.py), its [English Markdown report](./examples/08_inspect_report.result.md), and a [Japanese annotated report](./examples/08_inspect_report.result.ja.md). `--json` remains an alias for `--format json`.

## Pytest and CI

niltest complements pytest rather than replacing it. With `--niltest`, each declared case is collected as an independent pytest item and participates in normal reports, JUnit XML, and coverage. Without the flag, the plugin is inert.

```bash
pytest --niltest --niltest-module=your_package.specs
pytest --niltest --junitxml=report.xml --cov=your_package
```

```toml
[tool.pytest.ini_options]
niltest_modules = ["your_package.specs"]
```

## Zero-cost production path

For declaration-style specifications outside a function body, use `@docs`. In production mode, `@scenario` returns the original function with no runtime wrapper or niltest branch.

```python
from niltest import case, docs, scenario

@scenario("Shipping fee")
@docs(case("premium", given={"premium": True}, returns=0))
def shipping_fee(premium: bool) -> int:
    return 0 if premium else 500
```

## Localization

Japanese and English are built in. niltest detects the operating-system locale and falls back to English. Add languages with `register_locale()` and the validated locale template.

## Release provenance

PyPI distributions use Trusted Publishing and carry Sigstore attestations. GitHub Releases contain build-provenance attestations, and every distribution has SLSA Build Level 3 provenance.

```bash
gh attestation verify niltest-*.whl --repo disnana/niltest
gh attestation verify niltest-*.tar.gz --repo disnana/niltest
```

## Built with Codex and GPT-5.6

Codex and GPT-5.6 supported repository audit, API design, implementation, test diagnosis, packaging, localization, and documentation. Changes were reviewed through executable tests and CI.

## License

MIT © 2026 Disnana
