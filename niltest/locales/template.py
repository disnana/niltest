"""Copy this module when adding a built-in niltest locale.

Replace every value, then import and register the catalog at application
startup with ``niltest.register_locale("<locale>", MESSAGES)``.
"""

MESSAGES = {
    "scenario": "TODO",
    "description": "TODO",
    "returns": "TODO",
    "raises": "TODO",
    "type_check_only": "TODO",
    "validator": "TODO",
    "no_cases": "TODO",
    "result": "TODO {passed} TODO {failed} TODO",
    "value_mismatch": "TODO\n  expected={expected!r}\n  actual  ={actual!r}",
    "type_mismatch": "TODO actual={actual}, expected={expected}",
    "fields_mismatch": "TODO\n  expected={expected}\n  actual  ={actual}",
    "validator_false": "TODO\n  actual={actual!r}",
    "validator_error": "TODO {error}",
    "inspect_scenario": "TODO",
    "inspect_returns": "TODO",
    "inspect_cases": "TODO {count} TODO {mockable}",
    "inspect_untyped": "TODO",
    "inspect_none": "TODO",
    "inspect_valid": "TODO",
    "inspect_invalid": "TODO",
}
