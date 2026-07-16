from __future__ import annotations

import inspect
from typing import Any, get_type_hints

from . import _config
from ._compare import can_use_as_mock, format_returns
from ._i18n import translate
from ._typing import format_type_hint, validate_case_inputs


def inspect_scenario(target: Any) -> dict[str, Any]:
    """Build a machine-readable description of one registered scenario."""
    original = getattr(target, "__niltest_original__", target)
    title = getattr(target, "__niltest_title__", original.__name__)
    get_cases = getattr(target, "__niltest_get_cases__", lambda: ())
    cases = get_cases()
    signature = inspect.signature(original)
    try:
        hints = get_type_hints(original, include_extras=True)
    except Exception:
        hints = dict(getattr(original, "__annotations__", {}))

    parameters = []
    untyped = []
    for name, parameter in signature.parameters.items():
        annotation = hints.get(name, parameter.annotation)
        if annotation is inspect.Parameter.empty:
            untyped.append(name)
        parameters.append(
            {
                "name": name,
                "type": format_type_hint(annotation),
                "required": parameter.default is inspect.Parameter.empty,
            }
        )

    case_descriptions = []
    for case in cases:
        issues = validate_case_inputs(original, case.given)
        case_descriptions.append(
            {
                "name": case.name,
                "description": case.desc,
                "given": case.given,
                "returns": format_returns(case.returns),
                "mockable": can_use_as_mock(case.returns),
                "valid": not issues,
                "issues": list(issues),
            }
        )

    return {
        "title": title,
        "function": f"{original.__module__}.{original.__qualname__}",
        "signature": f"{original.__name__}{signature}",
        "parameters": parameters,
        "returns": format_type_hint(hints.get("return", signature.return_annotation)),
        "untyped_parameters": untyped,
        "case_count": len(cases),
        "mockable_cases": sum(case["mockable"] for case in case_descriptions),
        "valid": bool(cases) and all(case["valid"] for case in case_descriptions),
        "cases": case_descriptions,
    }


def inspect_scenarios(targets: list[Any]) -> dict[str, Any]:
    scenarios = [inspect_scenario(target) for target in targets]
    return {
        "valid": bool(scenarios) and all(scenario["valid"] for scenario in scenarios),
        "scenario_count": len(scenarios),
        "scenarios": scenarios,
    }


def format_inspection(report: dict[str, Any]) -> str:
    """Format an inspection report for people reading it in a terminal."""
    lines: list[str] = []
    for scenario in report["scenarios"]:
        lines.append(scenario["signature"])
        lines.append(f"  {translate(_config._LANGUAGE, 'inspect_scenario')}: {scenario['title']}")
        lines.append(f"  {translate(_config._LANGUAGE, 'inspect_returns')}: {scenario['returns']}")
        lines.append(
            "  "
            + translate(
                _config._LANGUAGE,
                "inspect_cases",
                count=scenario["case_count"],
                mockable=scenario["mockable_cases"],
            )
        )
        untyped = scenario["untyped_parameters"]
        untyped_value = (
            ", ".join(untyped) if untyped else translate(_config._LANGUAGE, "inspect_none")
        )
        lines.append(f"  {translate(_config._LANGUAGE, 'inspect_untyped')}: {untyped_value}")
        for case in scenario["cases"]:
            marker = translate(
                _config._LANGUAGE,
                "inspect_valid" if case["valid"] else "inspect_invalid",
            )
            lines.append(f"    [{marker}] {case['name']} -> {case['returns']}")
            for issue in case["issues"]:
                lines.append(f"      {issue}")
        lines.append("")
    return "\n".join(lines).rstrip()
