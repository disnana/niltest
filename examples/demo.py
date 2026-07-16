"""A fast, dependency-free demo used by the README and judges."""
from __future__ import annotations

from niltest import expect, scenario


@scenario("Shipping fee / 配送料")
def shipping_fee(subtotal: int, premium: bool = False) -> int:
    if expect:
        expect.case(
            "Premium shipping / プレミアム会員",
            desc="Premium members always receive free shipping.",
            given={"subtotal": 1_000, "premium": True},
            returns=0,
        )
        expect.case(
            "Standard shipping / 通常配送",
            desc="Orders below 5,000 pay a fixed shipping fee.",
            given={"subtotal": 1_000, "premium": False},
            returns=500,
        )
        expect.case(
            "Free threshold / 送料無料ライン",
            desc="Orders of 5,000 or more receive free shipping.",
            given={"subtotal": 5_000, "premium": False},
            returns=0,
        )

    if premium or subtotal >= 5_000:
        return 0
    return 500
