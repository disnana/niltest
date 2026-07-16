from __future__ import annotations


def test_language_detection_falls_back_to_english(monkeypatch):
    import niltest._config as config

    monkeypatch.delenv("NILTEST_LANGUAGE", raising=False)
    monkeypatch.setattr(config.locale, "getlocale", lambda: (None, None))
    assert config._detect_language() == "en"


def test_language_detection_prefers_explicit_environment(monkeypatch):
    import niltest._config as config

    monkeypatch.setenv("NILTEST_LANGUAGE", "ja-JP")
    monkeypatch.setattr(config.locale, "getlocale", lambda: ("en_US", "UTF-8"))
    assert config._detect_language() == "ja"
