from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar, overload

from ._case import MISSING, ExceptionTypes, _Case, _Missing, caller_location

F = TypeVar("F", bound=Callable[..., Any])


@overload
def case(
    name: str,
    *,
    given: dict[str, Any],
    returns: Any,
    raises: None = None,
    match: None = None,
    desc: str = "",
) -> _Case: ...


@overload
def case(
    name: str,
    *,
    given: dict[str, Any],
    returns: _Missing = MISSING,
    raises: ExceptionTypes,
    match: str | None = None,
    desc: str = "",
) -> _Case: ...


def case(
    name: str,
    *,
    given: dict[str, Any],
    returns: Any = MISSING,
    raises: ExceptionTypes | None = None,
    match: str | None = None,
    desc: str = "",
) -> _Case:
    """Create a case for the declaration-style ``@docs`` API."""
    source_file, source_line = caller_location()
    return _Case(
        name,
        desc=desc,
        given=given,
        returns=returns,
        raises=raises,
        match=match,
        source_file=source_file,
        source_line=source_line,
    )


def docs(*cases: _Case) -> Callable[[F], F]:
    """Attach cases without wrapping or executing the decorated function."""

    def decorator(func: F) -> F:
        setattr(func, "__niltest_cases__", tuple(cases))  # noqa: B010
        return func

    return decorator
