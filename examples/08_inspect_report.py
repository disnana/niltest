"""A small module intended for ``niltest inspect`` demonstrations."""

from niltest import case, docs, scenario


@scenario("Subscription quote")
@docs(
    case(
        "team annual plan",
        desc="Annual teams receive a 20% discount.",
        given={"plan": "team", "seats": 3, "annual": True},
        returns=288,
    ),
    case(
        "at least one seat",
        desc="A subscription cannot be created without seats.",
        given={"plan": "starter", "seats": 0, "annual": False},
        raises=ValueError,
        match="at least one",
    ),
)
def subscription_quote(plan: str, seats: int, annual: bool = False) -> int:
    """Return a subscription quote in US dollars."""
    if seats < 1:
        raise ValueError("at least one seat is required")
    unit_price = {"starter": 12, "team": 30}[plan]
    total = unit_price * seats * 12
    return int(total * 0.8) if annual else total
