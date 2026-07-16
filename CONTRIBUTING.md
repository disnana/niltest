# Contributing

Thank you for helping improve niltest.

1. Fork the repository and create a focused branch.
2. Create and activate a Python 3.10+ virtual environment.
3. Run `python -m pip install -e ".[dev]"`.
4. Add tests for behavior changes.
5. Run `python -m pytest` and `niltest run examples.demo --language en`.
6. Open a pull request explaining the problem and the chosen behavior.

For a new locale, copy `niltest/locales/template.py`, translate every value without changing placeholder names, and add detection/translation tests.
