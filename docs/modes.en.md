# Operating modes

| Mode | Setting | Behaviour |
|---|---|---|
| Production | `PRODUCTION=true` before import | The decorator is a no-op and `if expect:` is false. |
| Mock | `MODE=MOCK` | A case whose `given` exactly matches the call returns its fixed value. |
| Test | `MODE=TEST` plus `run_tests()` | Each case calls the real implementation and compares its result. |

Use production mode as an environment setting, not as a late runtime switch: decorators are evaluated when their module is imported.
