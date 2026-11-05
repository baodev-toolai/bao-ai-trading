# Work200 GitHub PR evidence — 2026-11-05

- Source: Work200_Paper_Backtest_v0_4_TEST.zip, 35 files; selected isolated 18 package/test/profile files.
- Local full source zip: `PYTHONPATH=. python -m pytest -q` -> 71 passed in 0.47s, exit code 0.
- Local isolated source excluding `tests/test_reference_integrity.py` -> 68 passed in 0.12s, exit code 0.
- CI to run on GitHub: Python 3.11 and 3.13 against 68 tests; Node.js syntax checks. CI results are NOT VERIFIED at commit creation.
- Original reference integrity test omitted because the large TradingView/MQL5 reference binaries/source are NOT imported in this PR. Do not claim full 71 tests ran in GitHub CI.
- Existing Node.js server, webhook and execution settings: UNCHANGED. No secret requirements, no external network broker calls.
- Datadog workflow deleted on feature branch as explicitly requested; not on main until PR merge. No replacement Datadog secrets needed.
- Scope: REVIEW_ONLY / BTCUSDT SPOT PAPER historical simulator; XAUUSD CFD profile only for future isolated development.
- Missing: durable event replay, daily rollover risk limit, max drawdown kill, authenticated live webhook bridge, MT5 compile, full backtest evidence with historical market data.
- Do not merge until reviewer confirms safety/diff and CI logs.
