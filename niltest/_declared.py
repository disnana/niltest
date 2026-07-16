from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar

from ._case import _Case

F = TypeVar("F", bound=Callable[..., Any])


def case(
    name: str,
    *,
    given: dict[str, Any],
    returns: Any,
    desc: str = "",
) -> _Case:
    """Create a case for the declaration-style ``@docs`` API."""
    return _Case(name, desc=desc, given=given, returns=returns)


def docs(*cases: _Case) -> Callable[[F], F]:
    """Attach cases without wrapping or executing the decorated function."""

    def decorator(func: F) -> F:
        setattr(func, "__niltest_cases__", tuple(cases))  # noqa: B010
        return func

    return decorator
