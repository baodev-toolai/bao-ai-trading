from datetime import datetime, timedelta, timezone
from decimal import Decimal as D
import pytest
from crypto_bot.backtest import replay_spot
from crypto_bot.models import Candle, Side
from crypto_bot.risk import RiskLimits
from crypto_bot.strategy import MovingAverageCross

T = datetime(2026, 10, 1, tzinfo=timezone.utc)

def bars(close_prices, *, gap_at=None):
    result=[]
    for i,v in enumerate(close_prices):
        price=D(str(v)); minute=i*15+(15 if gap_at is not None and i>=gap_at else 0)
        result.append(Candle("BTCUSDT",T+timedelta(minutes=minute),price,price,price,price,D(1)))
    return result

class Once:
    def on_candle(self, history):
        return Side.BUY if len(history)==1 else (Side.SELL if len(history)==3 else None)

class NoTrade:
    def on_candle(self, history):
        return None

class ForeverBuy:
    def on_candle(self, history):
        return Side.BUY

class Bad:
    def on_candle(self, history):
        return "BUY"

def test_next_open_no_lookahead():
    r=replay_spot(bars([100,110,120,90,80]),Once(),fee_rate=D(0),slippage_rate=D(0),allocation=D('0.5'))
    assert len(r.fills)==2
    assert r.fills[0].price==D(110)
    assert r.fills[1].price==D(90)
    assert r.equity_curve[0].position_quantity==0
    assert r.equity_curve[1].position_quantity>0

def test_fee_and_slippage_accounted_and_equality():
    r=replay_spot(bars([100,100,100,100]),Once(),allocation=D('0.5'))
    assert r.total_fees>0
    assert r.net_profit < 0
    assert r.ending_equity==r.equity_curve[-1].cash
    assert r.turnover>0

def test_no_trades_flat_equity():
    r=replay_spot(bars([100,110,120]),NoTrade())
    assert r.net_profit==0 and r.max_drawdown==0 and len(r.fills)==0
    assert r.as_report()['paper_only'] is True

def test_deterministic_and_stateless():
    data=bars([100,100,100,99,98,101,104,108,95,94])
    s=MovingAverageCross(2,3)
    x=replay_spot(data,s)
    y=replay_spot(data,s)
    assert x==y

def test_holdings_prevent_spot_short():
    class FirstSell:
        def on_candle(self,history): return Side.SELL
    r=replay_spot(bars([100,100,100]),FirstSell())
    assert not r.fills

def test_strict_gap_rejection():
    with pytest.raises(ValueError,match='missing or irregular'):
        replay_spot(bars([100,100,100,100],gap_at=2),NoTrade())

def test_reject_malformed_allocation():
    with pytest.raises(ValueError): replay_spot(bars([100]),NoTrade(),allocation=D('1.01'))


def test_reject_unknown_strategy_action():
    with pytest.raises(ValueError,match='Side'):
        replay_spot(bars([100]),Bad())


def test_risk_order_notional_rejected_no_fill():
    limits=RiskLimits(D('1'),D('1'),D('999999'))
    r=replay_spot(bars([100,100,100]),ForeverBuy(),risk_limits=limits)
    assert len(r.fills)==0 and r.rejected_orders==2


def test_drawdown_and_report():
    r=replay_spot(bars([100,100,120,60,60]),ForeverBuy(),allocation=D('0.5'),fee_rate=D(0),slippage_rate=D(0))
    assert D(0)<r.max_drawdown<D(1)
    assert r.as_report()['max_drawdown']==str(r.max_drawdown)


def test_allocation_one_preserves_nonnegative_cash():
    r=replay_spot(bars([100,100,100,100]),ForeverBuy(),allocation=D(1))
    assert all(p.cash>=0 for p in r.equity_curve)