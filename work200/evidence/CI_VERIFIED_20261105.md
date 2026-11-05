# Work 200 — Verified CI Evidence / Biên bản kiểm chứng CI
Date / Ngày: 2026-11-05
Repository: `baodev-toolai/bao-ai-trading`
Scope: commit `09f3fff573ac5891277c85f5916a76254c72f0b6` on `main`

## VERIFIED (GitHub Actions only) / Đã xác minh (chỉ CI)
- Run: https://github.com/baodev-toolai/bao-ai-trading/actions/runs/42005943640
- Python 3.11 job ID `127172585039`: SUCCESS; command `python -m compileall -q crypto_bot` succeeded, `python -m pytest -q tests` -> **68 passed in 0.10s**, exit 0 (job completed successfully).
- Python 3.13 job ID `127172585696`: SUCCESS; command `python -m compileall -q crypto_bot` succeeded, `python -m pytest -q tests` -> **68 passed in 0.12s**, exit 0 (job completed successfully).
- Existing Node.js syntax job ID `127172585794`: SUCCESS, syntax check only (no server startup).
- These are GitHub-hosted workflow results at the specified commit, NOT Sandbox pytest and NOT live/paper execution E2E.

## NOT_RUN / BLOCKED — no automatic PASS
| Component / Thành phần | Status | Missing evidence / Bằng chứng còn thiếu |
|---|---|---|
| BX42 pipe/JSON parser compatibility | NOT_RUN | Strict parser contract + accept/reject tests and full CI log for BX42 |
| Signal -> risk guard -> paper fill E2E | NOT_RUN | End-to-end synthetic BUY/SELL, reject, fees/slippage, ledger + logs |
| Dashboard API paper read-only | NOT_RUN | Backend/browser E2E, health/stale/disconnected tests |
| MT5 v0.1 | BLOCKED | MetaEditor F7 compile log, Strategy Tester report and manual confirmation |
| Sandbox pytest for separate Work 200 environment | NOT_RUN | Command, output and exit code from actual Sandbox |
| Broker execution/live trading | BLOCKED | Explicitly excluded; no real orders, credentials or execution bridge authorized |

## Safety / Quy tắc an toàn
- REVIEW_ONLY / paper-first. Never create or transmit real broker orders.
- Fail closed on unknown modes, invalid or malformed signals, unsupported parser payloads and any route that could enable live execution.
- CI SUCCESS proves only the tests executed by that CI workflow passed. It does not prove Sandbox pytest, paper/live E2E, MT5 compilation, strategy profitability or production readiness.
- No main merge or release without a separate human review/approval; this evidence note is documentation, not release authorization.

## Next verification steps / Bước tiếp theo
1. Implement isolated BX42 parser contract tests with valid/invalid pipe/JSON fixtures; ensure BACKTEST/PAPER/SL_UPDATE never become executable broker orders.
2. Add independent deterministic paper E2E tests for BUY, SELL, risk reject, fees/slippage and ledger.
3. Verify API read-only browser/backend health and stop-button semantics; label UI-only Stop, not a backend kill switch.
4. Collect MetaEditor F7 + Strategy Tester evidence on an MT5-capable Windows/demo environment.
5. Record per-run branch, commit SHA, command, exit code, timestamp and log/artifact links before marking each gate VERIFIED.
