from __future__ import annotations

import niltest
import pytest


@pytest.fixture(autouse=True)
def reset_language():
    import niltest._config as config

    previous = config._LANGUAGE
    config._LANGUAGE = "ja"
    yield
    config._LANGUAGE = previous


def test_english_output_and_docstring():
    from niltest import expect, scenario

    niltest.configure(production=False, mode="MOCK", language="en")

    @scenario("Greeting")
    def greet(name: str) -> str:
        if expect:
            expect.case("Known name", desc="A fixed greeting", given={"name": "Ada"}, returns="Hi Ada")
        return f"Hi {name}"

    assert greet("Ada") == "Hi Ada"
    assert "Description" in (greet.__doc__ or "")


def test_custom_locale_requires_complete_catalog():
    with pytest.raises(ValueError, match="missing"):
        niltest.register_locale("incomplete", {"scenario": "Scenario"})


def test_unknown_language_is_rejected():
    with pytest.raises(ValueError, match="Unknown language"):
        niltest.configure(language="not-registered")
