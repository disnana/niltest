from niltest import case, docs, scenario


@scenario("Shipping fee")
@docs(
    case("Premium member", given={"premium": True}, returns=0),
    case("Standard member", given={"premium": False}, returns=500),
)
def shipping_fee(premium: bool) -> int:
    return 0 if premium else 500


if __name__ == "__main__":
    shipping_fee.run_tests()  # type: ignore[attr-defined]
