"""Exception specifications and pytest integration introduced in niltest 1.2."""

import niltest
from niltest import case, docs, scenario

if __name__ == "__main__":
    niltest.configure(mode="test")


@scenario("Withdraw funds")
@docs(
    case("valid", given={"balance": 100, "amount": 40}, returns=60),
    case(
        "insufficient funds",
        given={"balance": 100, "amount": 150},
        raises=ValueError,
        match="insufficient",
    ),
)
def withdraw(balance: int, amount: int) -> int:
    if amount > balance:
        raise ValueError("insufficient funds")
    return balance - amount


if __name__ == "__main__":
    niltest.run_tests(withdraw)
