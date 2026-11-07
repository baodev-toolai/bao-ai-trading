# Work 200 Paper E2E v0.5 — REVIEW_ONLY

This change adds a **strictly offline synthetic** BTCUSDT/OKX/SPOT/15m pipeline with the path:
`parse_signal -> SQLite review journal -> RiskManager -> simulated PaperBroker fill`.

SQLite rejects replayed event IDs and permanently blocks sessions from restarting or running concurrently on the same journal file until a portfolio-reconciliation mechanism exists. A crash between fill and journal update remains unreconciled and **must not** be replayed. No HTTP/webhook or broker service calls exist.

`PaperEquityGuard` separately observes trusted mark-to-market equity with daily UTC first-observation baseline and peak drawdown. Reaching either threshold triggers the paper-only kill switch and cancels queued paper proposals. **This observer has not yet been wired into the chronological backtest engine or a terminal.** A missing observation or a gap can cause unexpected loss.

All prices in `OfflinePaperScenario.apply` are manually supplied **synthetic** prices; this is not an authenticated real market feed. No XAUUSD CFD, MT5, source authentication, persistent account/portfolio, auto recovery, or live trading. Existing Node.js server/webhook is unchanged.

Tests: `cd work200 && python -m pytest -q tests && python -m compileall -q crypto_bot`. GitHub CI checks Python 3.11/3.13.

**Do not merge automatically**; independent review remains mandatory.
