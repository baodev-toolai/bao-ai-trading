# Security and trading boundary

All source is research-only. Do not store API secrets or MetaTrader credentials in this repository.

- The Python `PaperBroker` is for simulated OKX/BTCUSDT SPOT only and cannot short spot.
- The Pine and MQL5 files are strategy references, **not** authorized execution adapters.
- MQL5 V0.1 is a signal-planning EA; no MetaEditor compile evidence is included.
- No live REST/WebSocket brokerage connections, withdrawals, or trade execution controls are permitted.
- `SignalIntake` uses in-memory de-duplication only; it is not authenticated or restart-safe.
- The risk-loss figure currently covers realized lifetime PnL, not a validated calendar-day loss limit.
- Any transition to demo order placement must first pass documented account/risk gates.
- Work 200 runtime tests, TradingView compile, MetaEditor compile and end-to-end broker parity require separate evidence.