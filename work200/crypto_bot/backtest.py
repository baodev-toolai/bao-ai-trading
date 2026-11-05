"""Deterministic, single-symbol SPOT-only historical replay; no order APIs.

Signal is calculated after bar t closes, then filled at bar t+1 OPEN. The
simulator does not model overnight financing, intrabar stops, or live trading.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Protocol

from .data_validation import validate_candles
from .models import Candle, Fill, OrderRequest, Side
from .paper_broker import PaperBroker
from .risk import RiskLimits, RiskManager


class SignalStrategy(Protocol):
    def on_candle(self, history: list[Candle]) -> Side | None: ...


@dataclass(frozen=True)
class EquityPoint:
    timestamp: datetime
    cash: Decimal
    position_quantity: Decimal
    close: Decimal
    equity: Decimal
    drawdown: Decimal


@dataclass(frozen=True)
class BacktestResult:
    starting_cash: Decimal
    ending_equity: Decimal
    net_profit: Decimal
    total_return: Decimal
    max_drawdown: Decimal
    total_fees: Decimal
    turnover: Decimal
    fills: tuple[Fill, ...]
    equity_curve: tuple[EquityPoint, ...]
    rejected_orders: int
    strategy_name: str

    def as_report(self) -> dict[str, str | int | bool]:
        return {
            "engine": "spot-paper-sequential-v0.4",
            "strategy": self.strategy_name,
            "starting_cash": str(self.starting_cash),
            "ending_equity": str(self.ending_equity),
            "net_profit": str(self.net_profit),
            "total_return": str(self.total_return),
            "max_drawdown": str(self.max_drawdown),
            "total_fees": str(self.total_fees),
            "turnover": str(self.turnover),
            "fills": len(self.fills),
            "equity_points": len(self.equity_curve),
            "rejected_orders": self.rejected_orders,
            "live_execution": False,
            "paper_only": True,
        }


def replay_spot(
    candles: list[Candle], strategy: SignalStrategy, *,
    starting_cash: Decimal = Decimal("10000"),
    allocation: Decimal = Decimal("0.25"),
    fee_rate: Decimal = Decimal("0.001"),
    slippage_rate: Decimal = Decimal("0.0005"),
    timeframe: timedelta = timedelta(minutes=15),
    risk_limits: RiskLimits | None = None,
) -> BacktestResult:
    """Run spot-only sequential replay with next-bar open fills.

    Explicitly single-symbol fixed-cadence data; gaps are rejected rather
    than silently filled. 24x7 fixed cadence suits crypto, NOT XAUUSD sessions.
    Long-only strategy: BUY if flat, SELL closes holdings, repeated same-side
    signals are ignored. No per-day roll-over risk is claimed.
    """
    if not isinstance(allocation, Decimal) or not allocation.is_finite() or not 0 < allocation <= 1:
        raise ValueError("allocation must be in (0, 1]")
    bars = list(validate_candles(candles, timeframe=timeframe))
    limits = risk_limits or RiskLimits(Decimal("1e20"), Decimal("1e20"), Decimal("1e20"))
    risk = RiskManager(limits)
    broker = PaperBroker(risk, fee_rate=fee_rate, slippage_rate=slippage_rate,
                         starting_cash=starting_cash)
    curve: list[EquityPoint] = []
    peak = starting_cash
    max_dd = Decimal("0")
    rejected = 0
    next_side: Side | None = None
    for i, bar in enumerate(bars):
        # The pending decision only uses candles ending at the prior bar.
        if next_side is not None:
            qty_held = broker.positions.get(bar.symbol, Decimal("0"))
            if next_side == Side.BUY and qty_held == 0 and not risk.halted:
                # Buy-side slippage and entry commission are budgeted in quantity.
                expected_price = bar.open * (Decimal("1") + slippage_rate)
                budget = broker.cash * allocation
                qty = budget / (expected_price * (Decimal("1") + fee_rate))
                if qty > 0:
                    try:
                        broker.submit(OrderRequest(bar.symbol, Side.BUY, qty), bar.open)
                    except PermissionError:
                        rejected += 1
            elif next_side == Side.SELL and qty_held > 0:
                try:
                    broker.submit(OrderRequest(bar.symbol, Side.SELL, qty_held), bar.open)
                except PermissionError:
                    rejected += 1
        qty = broker.positions.get(bar.symbol, Decimal("0"))
        eq = broker.cash + qty * bar.close
        if eq > peak:
            peak = eq
        drawdown = (peak - eq) / peak if peak > 0 else Decimal("0")
        max_dd = max(max_dd, drawdown)
        curve.append(EquityPoint(bar.timestamp, broker.cash, qty, bar.close, eq, drawdown))
        # Signals are only emitted after the current CLOSED candle.
        next_side = strategy.on_candle(bars[:i + 1])
        if next_side is not None and not isinstance(next_side, Side):
            raise ValueError("strategy must return Side or None")
    ending = curve[-1].equity
    fees = sum((fill.fee for fill in broker.fills), Decimal("0"))
    turnover = sum((fill.price * fill.quantity for fill in broker.fills), Decimal("0"))
    return BacktestResult(starting_cash, ending, ending - starting_cash,
                          (ending - starting_cash) / starting_cash if starting_cash > 0 else Decimal("0"),
                          max_dd, fees, turnover, tuple(broker.fills), tuple(curve),
                          rejected, type(strategy).__name__)