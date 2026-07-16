# niltest

niltest keeps lightweight executable specifications, development mocks, and checks next to a Python function. Japanese documentation is available in [README.md](./README.md).

```python
import niltest
from niltest import expect, scenario

@scenario("Fetch a user")
def get_user(user_id: int) -> dict:
    if expect:
        expect.case("Known user", given={"user_id": 1}, returns={"id": 1, "name": "Alice"})
    return load_user(user_id)

niltest.configure(mode="MOCK", language="en")
assert get_user(1) == {"id": 1, "name": "Alice"}

niltest.configure(mode="TEST")
niltest.run_tests(get_user)
```

## Documentation

| English | Japanese |
|---|---|
| [Concepts](./concepts.en.md) | [概要](./concepts.md) |
| [API reference](./api.en.md) | [API リファレンス](./api.md) |
| [Operating modes](./modes.en.md) | [動作モード](./modes.md) |
| [Localization](./i18n.md) | [多言語化](./i18n.md) |
