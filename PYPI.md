# niltest

**Executable specifications, fixed development mocks, and lightweight checks—next to the Python function they describe.**

[日本語](#日本語) · [Documentation](https://niltest.disnana.com/docs/) · [GitHub](https://github.com/disnana/niltest/) · [Issues](https://github.com/disnana/niltest/issues)
<!-- AI integration context: https://niltest.disnana.com/docs/ai-context.json -->

niltest lets one `expect.case()` definition serve three purposes:

- readable behavior close to the implementation;
- a fixed mock when databases or external APIs are unavailable;
- an executable check against the real function.

It has no runtime dependencies and supports Python 3.10+ on Windows, macOS, and Linux.
Pydantic-backed type validation is available through the optional `niltest[pydantic]` extra.

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
from niltest import Mode, expect, scenario

niltest.configure(mode=Mode.MOCK)  # Configure before @scenario is evaluated.

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


assert shipping_fee(1_000, premium=True) == 0

niltest.configure(mode=Mode.TEST)
result = niltest.run_tests(shipping_fee)
assert result.success
```

## CLI and CI

```bash
niltest run your_package.specs --language en
niltest run your_package.specs --json
```

The CLI exits with `0` when all cases pass, `1` for specification failures, and `2` for usage or import errors. JSON output and the structured `RunResult` API make niltest easy to compose with CI and other developer tools.

## Selecting a mode from Python

Use the `Mode` enum for completion and type checking. String values remain available when brevity or compatibility matters.

```python
from niltest import Mode, configure

configure(mode=Mode.TEST)   # Recommended
configure(mode="test")      # Also supported
```

## Expectations

`returns` supports:

- plain values and collections;
- dataclass instances;
- Pydantic models;
- type-only checks such as `returns=UserData`;
- custom validators such as `returns=lambda result: result["count"] > 0`;
- synchronous and asynchronous functions.

## Typed specifications and inspection

Version 1.1 adds `conforms_to()`, backed by Pydantic's `TypeAdapter`. It validates
models and arbitrary annotations such as `list[User]`, unions, and `Annotated`
constraints. During specification execution, case inputs are checked against the
function signature and annotations, then normalized (for example, a dictionary can
become a Pydantic model) before the implementation runs. Normal application calls
and production mode inputs are never transformed by niltest.

```python
from niltest import case, conforms_to, docs, scenario

@scenario("User lookup")
@docs(case("existing", given={"user_id": 1}, returns=conforms_to(User)))
def fetch_user(user_id: int) -> dict[str, object]:
    return {"id": user_id, "name": "Alice"}
```

Use `niltest inspect your_package.services` as a compact architecture map. Replace
`your_package.services` with an importable module path such as
`your_package/services.py`. Inspect imports the module and lists registered
scenarios; it does not execute their cases.

```bash
niltest inspect your_package.services                 # terminal-friendly text
niltest inspect your_package.services --format json   # CI and other tools
niltest inspect your_package.services --format markdown # reviews and design docs
```

`--json` remains a compatibility alias for `--format json`.

The repository includes an [inspectable example](https://github.com/disnana/niltest/blob/main/examples/08_inspect_report.py)
with [English](https://github.com/disnana/niltest/blob/main/examples/08_inspect_report.result.md)
and [Japanese](https://github.com/disnana/niltest/blob/main/examples/08_inspect_report.result.ja.md) Markdown reports.

## Pytest integration and exception specifications

Version 1.2 exposes each niltest case as an individual pytest item. The plugin is
inert unless `--niltest` is present, so existing pytest behavior is unchanged.

```bash
pytest --niltest --niltest-module=your_package.specs
pytest --niltest --junitxml=report.xml --cov=your_package
```

```toml
[tool.pytest.ini_options]
niltest_modules = ["your_package.specs"]
```

Use exactly one of `returns` or `raises`. `match` is a regular expression applied
to the exception message. Exception cases validate the real implementation and
never act as fixed mocks.

```python
@scenario("Withdraw funds")
@docs(case(
    "insufficient funds",
    given={"balance": 100, "amount": 150},
    raises=ValueError,
    match="insufficient",
))
def withdraw(balance: int, amount: int) -> int:
    if amount > balance:
        raise ValueError("insufficient funds")
    return balance - amount
```

Inspection reports are available as text, JSON, or portable Markdown:

```bash
niltest inspect your_package.specs --format markdown
```

## Production path

`NILTEST_MODE=production` is the safe default. Set `NILTEST_MODE=test` or `NILTEST_MODE=mock` before importing decorated modules when you want niltest's development features. In production mode, `@scenario` returns the original function without creating a wrapper. The explicit `if expect:` truth check remains; niltest documents this measurable cost instead of claiming absolute zero overhead.

For zero niltest cost at function-call time, use the declaration-style API. The existing inline API remains fully supported.

```python
from niltest import case, docs, scenario

@scenario("Shipping fee")
@docs(case("Premium", given={"premium": True}, returns=0))
def shipping_fee(premium: bool) -> int:
    return 0 if premium else 500
```

With the default `NILTEST_MODE=production`, this returns the original function: no wrapper and no `if expect:` branch in its body.

## Localization

Japanese and English are built in. niltest detects the OS locale, falls back to English, and exposes `register_locale()` plus a validated template for additional languages.

## Verifying release provenance

Official wheel and source distributions are published through PyPI Trusted Publishing and carry Sigstore digital attestations. GitHub Releases contain the same files with GitHub build-provenance attestations tied to the source commit and CI workflow. An isolated, trusted SLSA generator also produces non-forgeable SLSA Build Level 3 provenance for every distribution.

After downloading a release asset, verify its origin with the GitHub CLI:

```bash
gh attestation verify niltest-*.whl --repo disnana/niltest
gh attestation verify niltest-*.tar.gz --repo disnana/niltest
```

For strict SLSA verification, download the matching `.intoto.jsonl` file from the GitHub Release and use `slsa-verifier`:

```bash
slsa-verifier verify-artifact niltest-*.whl \
  --provenance-path multiple.intoto.jsonl \
  --source-uri github.com/disnana/niltest \
  --source-branch main
```

Verification confirms provenance; it does not replace reviewing the package or its dependencies for your use case.

For Japanese documentation, see the [Japanese README](https://github.com/disnana/niltest/blob/main/README.ja.md) and [Japanese docs](https://niltest.disnana.com/docs/).

MIT © 2026 Disnana
