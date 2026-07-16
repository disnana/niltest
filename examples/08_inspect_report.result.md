# niltest specification report

Generated with:

```bash
niltest inspect examples.08_inspect_report --format markdown
```

## `subscription_quote(plan: str, seats: int, annual: bool = False) -> int`

**Scenario:** Subscription quote

**Returns:** `int`

| Case | Given | Expectation | Mockable | Valid | Source |
| --- | --- | --- | --- | --- | --- |
| team annual plan | {'plan': 'team', 'seats': 3, 'annual': True} | 288 | yes | yes | examples/08_inspect_report.py:8 |
| at least one seat | {'plan': 'starter', 'seats': 0, 'annual': False} | raises ValueError matching 'at least one' | no | yes | examples/08_inspect_report.py:14 |

> `Source` is an absolute path in the actual command output, so it will differ by machine.
