"""Pydantic-backed input and output specifications introduced in niltest 1.1."""

from typing import Annotated

from pydantic import BaseModel, Field

import niltest
from niltest import case, conforms_to, docs, scenario

if __name__ == "__main__":
    niltest.configure(mode="test")


class CreateUser(BaseModel):
    name: str
    age: Annotated[int, Field(ge=18)]


class User(BaseModel):
    id: int
    name: str


@scenario("Create an adult user")
@docs(
    case(
        "valid account",
        given={"payload": {"name": "Alice", "age": 20}},
        returns=conforms_to(User),
    )
)
def create_user(payload: CreateUser) -> dict[str, object]:
    return {"id": 1, "name": payload.name}


if __name__ == "__main__":
    niltest.run_tests(create_user)
