# Work 200 — Paper-only Python core (v0.4)

This isolated subproject preserves the existing Node.js Express webhook and does **not** connect to it. It is for safe review of historical BTCUSDT/OKX SPOT data.

## Local checks

```sh
cd work200
python -m pip install -e ".[test]"
python -m pytest -q tests
python -m compileall -q crypto_bot
```

The default SignalIntake has no authenticated external webhook or persistent replay store. The paper broker is long-only SPOT, and the backtest replays strictly chronological 15m candles, fills after bar close at next bar open, and models fixed fees/slippage. It does not simulate real ticks, broker orders, partial fills, stops, financing, MT5 or live execution. PnL/accounting is simplified, not a production portfolio.

`profiles/exness_xauusd_swing_m15.json` is an explicitly **non-executable CFD reference**; it must never be used with the SPOT-only backtester.

## Provenance and verification

Work200_Paper_Backtest_v0_4_TEST.zip was re-tested locally on 2026-11-05: 71/71 tests PASS, exit 0, including three tests of original Pine/MT5 reference files. The isolated source imported here excludes those large strategy reference files and their three reference-integrity tests. Thus the committed work200/ test set has **68 tests**, previously run locally and passing; GitHub Actions must run them independently. No GitHub CI PASS is claimed until workflow evidence appears.

## Release boundaries

NO LIVE BROKER ADAPTER. NO AUTOMATIC EXNESS/MT5 ORDER SENDING. No API keys, credentials, funded account access, durable idempotency, complete daily risk circuit breaker, or end-to-end paper signal integration. Keep REVIEW_ONLY. Changes should remain in a reviewable Pull Request until evidence is checked.
