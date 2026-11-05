"""Regression tests discovered during 2026-10-24 Work 200 review."""
from decimal import Decimal as D
from datetime import timedelta
import pytest
from crypto_bot.models import Side, OrderRequest
from crypto_bot.risk import RiskLimits, RiskManager
from crypto_bot.paper_broker import PaperBroker
from crypto_bot.strategy import MovingAverageCross
from crypto_bot.data_validation import validate_candles
from test_core import candle


def test_close_held_spot_is_allowed_when_position_at_limit():
    broker = PaperBroker(RiskManager(RiskLimits(D("200"), D("100"), D("40"))), fee_rate=D("0"), slippage_rate=D("0"))
    broker.submit(OrderRequest("BTCUSDT", Side.BUY, D("1")), D("100"))
    broker.submit(OrderRequest("BTCUSDT", Side.SELL, D("1")), D("100"))
    assert broker.positions == {}


def test_reductions_even_when_order_notional_exceeds_entry_limit():
    r = RiskManager(RiskLimits(D("10"), D("100"), D("20")))
    assert r.approve(OrderRequest("BTCUSDT", Side.SELL, D("1")), D("100"),
                     current_position_notional=D("100"), reduce_only=True)


def test_kill_activates_before_other_order_rejections():
    risk = RiskManager(RiskLimits(D("10"), D("100"), D("20")))
    assert not risk.approve(OrderRequest("BTCUSDT", Side.BUY, D("20")), D("100"), daily_pnl=D("-20"))
    assert risk.halted


def test_kill_cancels_pending_paper_orders():
    r = RiskManager(RiskLimits(D("1000"), D("2000"), D("100")))
    broker = PaperBroker(r)
    broker.queue_paper("evt-1", OrderRequest("BTCUSDT", Side.BUY, D("1")), D("100"))
    assert "evt-1" in broker.pending
    r.activate_kill_switch()
    assert not broker.pending
    with pytest.raises(PermissionError):
        broker.submit(OrderRequest("BTCUSDT", Side.BUY, D("1")), D("100"))


def test_exit_after_halt_allowed_but_new_exposure_blocked():
    r = RiskManager(RiskLimits(D("1000"), D("2000"), D("10")))
    broker = PaperBroker(r, fee_rate=D("0"), slippage_rate=D("0"))
    broker.submit(OrderRequest("BTCUSDT", Side.BUY, D("1")), D("100"))
    r.activate_kill_switch()
    broker.submit(OrderRequest("BTCUSDT", Side.SELL, D("1")), D("100"))
    assert not broker.positions
    with pytest.raises(PermissionError):
        broker.submit(OrderRequest("BTCUSDT", Side.BUY, D("1")), D("100"))


def test_spot_cannot_short():
    b = PaperBroker(RiskManager(RiskLimits(D("1000"), D("2000"), D("100"))))
    with pytest.raises(PermissionError, match="spot SELL"):
        b.submit(OrderRequest("BTCUSDT", Side.SELL, D("1")), D("100"))


def test_broker_uses_internal_pnl_and_trips_on_realized_loss():
    r = RiskManager(RiskLimits(D("1000"), D("2000"), D("10")))
    b = PaperBroker(r, fee_rate=D("0"), slippage_rate=D("0"))
    b.submit(OrderRequest("BTCUSDT", Side.BUY, D("1")), D("100"))
    b.submit(OrderRequest("BTCUSDT", Side.SELL, D("1")), D("80"))
    assert b.realized_pnl == D("-20")
    assert r.halted


def test_slippage_checked_at_expected_fill_price_not_reference():
    r = RiskManager(RiskLimits(D("100"), D("100"), D("10")))
    b = PaperBroker(r, fee_rate=D("0"), slippage_rate=D("0.05"))
    with pytest.raises(PermissionError):
        b.submit(OrderRequest("BTCUSDT", Side.BUY, D("1")), D("100"))


def test_cash_enforced_and_round_trip_fees_counted():
    b=PaperBroker(RiskManager(RiskLimits(D("200"),D("500"),D("50"))),fee_rate=D("0.01"),slippage_rate=D("0"),starting_cash=D("102"))
    b.submit(OrderRequest("BTCUSDT",Side.BUY,D("1")),D("100"))
    b.submit(OrderRequest("BTCUSDT",Side.SELL,D("1")),D("100"))
    assert b.realized_pnl==D("-2")
    assert b.cash==D("100")


def test_invalid_and_nonfinite_order_rejected():
    b=PaperBroker(RiskManager(RiskLimits(D("100"),D("200"),D("20"))))
    with pytest.raises(ValueError):
        b.submit(OrderRequest("BTCUSDT",Side.BUY,D("1")),D("NaN"))


def test_strategy_is_stateless_for_same_closed_history():
    cs=[candle(i,x) for i,x in enumerate(["10","10","10","10","10","10","11"])]
    st=MovingAverageCross(fast_window=2,slow_window=5)
    assert st.on_candle(cs) is Side.BUY
    assert st.on_candle(cs) is Side.BUY
    assert MovingAverageCross(2,5).on_candle(cs) is Side.BUY


def test_gap_detection_with_expected_timeframe():
    with pytest.raises(ValueError,match="irregular"):
        validate_candles([candle(0),candle(15),candle(45)],timeframe=timedelta(minutes=15))


def test_late_loss_check_blocks_when_over_limit_order():
    r=RiskManager(RiskLimits(D("10"),D("100"),D("20")))
    r.approve(OrderRequest("BTCUSDT",Side.BUY,D("100")),D("100"),daily_pnl=D("-20"))
    assert r.halted


def test_buy_rejected_above_position_cap():
    r=RiskManager(RiskLimits(D("500"),D("100"),D("20")))
    assert not r.approve(OrderRequest("BTCUSDT",Side.BUY,D("1")),D("50"),current_position_notional=D("60"))


def test_order_quantity_not_nan_infinite_or_negative():
    for v in ("NaN", "Infinity", "-1", "0"):
        with pytest.raises(ValueError):
            OrderRequest("BTCUSDT", Side.BUY, D(v))


def test_candle_price_and_volume_must_be_finite():
    from crypto_bot.models import Candle
    from datetime import datetime, timezone
    t = datetime(2026, 10, 24, tzinfo=timezone.utc)
    with pytest.raises(ValueError):
        Candle("BTCUSDT", t, D("NaN"), D("100"), D("100"), D("100"), D("1"))
    with pytest.raises(ValueError):
        Candle("BTCUSDT", t, D("100"), D("100"), D("100"), D("100"), D("Infinity"))


def test_broker_rejects_second_buy_using_internal_holdings():
    b = PaperBroker(RiskManager(RiskLimits(D("200"), D("100"), D("20"))), fee_rate=D("0"), slippage_rate=D("0"))
    b.submit(OrderRequest("BTCUSDT", Side.BUY, D("1")), D("80"))
    with pytest.raises(PermissionError):
        b.submit(OrderRequest("BTCUSDT", Side.BUY, D("1")), D("80"))
    assert b.positions["BTCUSDT"] == D("1")