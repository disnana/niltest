from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import Any, get_type_hints


@dataclass(frozen=True)
class TypeExpectation:
    """An expectation validated through Pydantic's ``TypeAdapter``."""

    type_hint: Any
    strict: bool = False


def conforms_to(type_hint: Any, *, strict: bool = False) -> TypeExpectation:
    """Require a result to conform to any Pydantic-compatible type hint."""
    return TypeExpectation(type_hint, strict)


def validate_type(value: Any, expectation: TypeExpectation) -> tuple[bool, str]:
    """Validate a value without making Pydantic a core runtime dependency."""
    try:
        from pydantic import TypeAdapter, ValidationError
    except ImportError:
        return False, "Pydantic is required; install niltest[pydantic]"

    try:
        TypeAdapter(expectation.type_hint).validate_python(value, strict=expectation.strict)
    except ValidationError as error:
        return False, str(error)
    except Exception as error:
        return False, f"{type(error).__name__}: {error}"
    return True, ""


def validate_case_inputs(func: Any, given: dict[str, Any]) -> tuple[str, ...]:
    """Check case inputs against a function signature and its annotations."""
    _, issues = prepare_case_inputs(func, given)
    return issues


def prepare_case_inputs(func: Any, given: dict[str, Any]) -> tuple[dict[str, Any], tuple[str, ...]]:
    """Validate and normalize case inputs using the function's annotations."""
    try:
        signature = inspect.signature(func)
        bound = signature.bind(**given)
    except TypeError as error:
        return dict(given), (str(error),)

    try:
        hints = get_type_hints(func, include_extras=True)
    except Exception:
        hints = dict(getattr(func, "__annotations__", {}))

    try:
        from pydantic import TypeAdapter, ValidationError
    except ImportError:
        return dict(given), ()

    issues: list[str] = []
    prepared = dict(given)
    for name, value in bound.arguments.items():
        annotation = hints.get(name, inspect.Parameter.empty)
        if annotation is inspect.Parameter.empty or annotation is Any:
            continue
        try:
            prepared[name] = TypeAdapter(annotation).validate_python(value)
        except ValidationError as error:
            issues.append(f"{name}: {error}")
        except Exception as error:
            issues.append(f"{name}: {type(error).__name__}: {error}")
    return prepared, tuple(issues)


def format_type_hint(type_hint: Any) -> str:
    """Return a compact, stable display name for a type annotation."""
    if type_hint is inspect.Signature.empty:
        return "untyped"
    return getattr(type_hint, "__name__", str(type_hint).replace("typing.", ""))
