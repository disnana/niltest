# API reference

## `configure(production=None, mode=None, language=None)`

Sets runtime options. `mode` is either `MOCK` or `TEST`; invalid values raise `ValueError`. If `language` is omitted, niltest uses the OS locale on Windows, macOS, or Linux, and falls back to English when unavailable or unsupported. It accepts regional forms such as `en-US`.

## `@scenario(title)`

Decorates a synchronous or asynchronous function. With `PRODUCTION=true` set before importing the decorated module, the original function is returned without a wrapper.

## `expect.case(name, *, desc="", given, returns)`

Registers an executable example. `given` is a keyword-argument dictionary. `returns` may be a value, a dataclass/Pydantic instance, a type, or a validator callable.

## `run_tests(*functions)`

Runs cases for the supplied decorated functions, or for all registered scenarios when no functions are supplied. It returns a `RunResult` with `success`, `passed`, `failed`, `scenarios`, and `to_dict()` while retaining human-readable terminal output.

## `register_locale(locale, messages, *, overwrite=False)`

Registers a complete custom message catalog. See [Localization](./i18n.md) for the required keys and an example.

## CLI

```bash
niltest run your_package.specs --language en
niltest run your_package.specs --json
```

Exit codes are `0` when all cases pass, `1` for specification failures, and `2` for usage or module-import errors. JSON mode suppresses progress text and writes one machine-readable result to standard output.
