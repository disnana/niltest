# Concepts and limitations

niltest is best suited to small, deterministic examples that explain a function's contract. It is not a replacement for pytest, integration tests, or explicit mocks where behaviour depends on I/O.

The library collects cases by executing the function once in a documentation scan. Keep `expect.case()` declarations at the top of the function, before side effects, and make the declaration block unconditional apart from `if expect:`. Production mode avoids the wrapper only when `PRODUCTION=true` is set before the decorated module is imported.
