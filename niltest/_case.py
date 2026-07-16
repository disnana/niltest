from __future__ import annotations

import inspect
import re
from pathlib import Path
from typing import Any


class _Missing:
    def __repr__(self) -> str:
        return "<missing>"


MISSING = _Missing()
ExceptionTypes = type[Exception] | tuple[type[Exception], ...]


def caller_location(depth: int = 1) -> tuple[str, int]:
    """Return the first user-facing frame above ``depth`` internal calls."""
    frame = inspect.currentframe()
    try:
        for _ in range(depth + 1):
            if frame is None:
                return "", 0
            frame = frame.f_back
        if frame is None:
            return "", 0
        return str(Path(frame.f_code.co_filename).resolve()), frame.f_lineno
    finally:
        del frame


class _Case:
    """One executable specification case."""

    __slots__ = (
        "desc",
        "given",
        "match",
        "name",
        "raises",
        "returns",
        "source_file",
        "source_line",
    )

    def __init__(
        self,
        name: str,
        *,
        desc: str = "",
        given: dict[str, Any],
        returns: Any = MISSING,
        raises: ExceptionTypes | None = None,
        match: str | None = None,
        source_file: str = "",
        source_line: int = 0,
    ) -> None:
        has_return = returns is not MISSING
        has_exception = raises is not None
        if has_return == has_exception:
            raise ValueError("case() requires exactly one of 'returns' or 'raises'.")
        if raises is not None:
            exception_types = raises if isinstance(raises, tuple) else (raises,)
            if not exception_types or any(
                not isinstance(exception, type) or not issubclass(exception, Exception)
                for exception in exception_types
            ):
                raise TypeError("raises must be an exception type or a non-empty tuple of them.")
        if match is not None and raises is None:
            raise ValueError("match can only be used together with raises.")
        if match is not None:
            try:
                re.compile(match)
            except re.error as error:
                raise ValueError(f"invalid exception match pattern: {error}") from error

        self.name = name
        self.desc = desc
        self.given = given
        self.returns = returns
        self.raises = raises
        self.match = match
        self.source_file = source_file
        self.source_line = source_line

    @property
    def source(self) -> str:
        if not self.source_file:
            return ""
        return f"{self.source_file}:{self.source_line}"
