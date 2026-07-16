from __future__ import annotations
from typing import Any


class _Case:
    """1つの仕様ケースを表すデータクラス。"""
    __slots__ = ("name", "desc", "given", "returns")

    def __init__(
        self,
        name: str,
        *,
        desc: str = "",
        given: dict[str, Any],
        returns: Any,
    ) -> None:
        self.name = name
        self.desc = desc
        self.given = given
        self.returns = returns
