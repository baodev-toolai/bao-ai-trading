"""Synthetic only; no webhook, network, MT5, or exchange."""
from datetime import datetime, timezone, timedelta
from decimal import Decimal as D
import pytest
from crypto_bot.paper_e2e import OfflinePaperScenario, PaperReplayBlocked
from crypto_bot.equity_guard import PaperEquityGuard
from crypto_bot.models import OrderRequest, Side
from crypto_bot.paper_broker import PaperBroker
from crypto_bot.risk import RiskLimits,RiskManager
from crypto_bot.signal_intake import SignalRejected,IntakePolicy
T=datetime(2026,11,8,tzinfo=timezone.utc)

def payload(event='BX428-20261108-001',side='BUY',**kwargs):
    x=dict(event_id=event,strategy='BX42MR',version='4.2.8',symbol='BTCUSDT',
           exchange='OKX',market='SPOT',timeframe='15m',side=side,
           event_time=T.isoformat(),candle_closed_at=T.isoformat(),
           closed_bar=True,execution_mode='SIGNAL_ONLY',live_execution=False,
           paper_only=True,entry='100',stop_loss='98',take_profit_1='102',
           take_profit_2='104',take_profit_3='106')
    if side=='SELL':
        x.update(stop_loss='102',take_profit_1='98',take_profit_2='96',take_profit_3='94')
    x.update(kwargs)
    return x

def test_buy_sell_simulated_fee_ledger(tmp_path):
    s=OfflinePaperScenario(tmp_path/'journal.db',starting_cash=D('1000'),
                           fee_rate=D('0.01'),slippage_rate=D('0'))
    a=s.apply(payload(),now=T,synthetic_price=D('100'),quantity=D('1'))
    b=s.apply(payload('BX428-20261108-002','SELL'),now=T,
              synthetic_price=D('110'),quantity=D('1'))
    assert a.status==b.status=='PAPER_FILLED'
    assert s.broker.realized_pnl==D('7.90') and s.broker.cash==D('1007.90')
    assert s.journal.status('BX428-20261108-001')=='PAPER_FILLED'

def test_spot_short_reject(tmp_path):
    s=OfflinePaperScenario(tmp_path/'journal.db')
    assert s.apply(payload(side='SELL'),now=T,synthetic_price=D('100'),quantity=D('1')).status=='PAPER_REJECTED'
    assert not s.broker.fills

def test_replay_and_restart_fail_closed(tmp_path):
    db=tmp_path/'journal.db'
    s=OfflinePaperScenario(db)
    s.apply(payload(),now=T,synthetic_price=D('100'),quantity=D('1'))
    with pytest.raises(PaperReplayBlocked):
        s.apply(payload(),now=T,synthetic_price=D('100'),quantity=D('1'))
    with pytest.raises(PaperReplayBlocked):
        OfflinePaperScenario(db)

def test_parallel_claim_fails_before_fill(tmp_path):
    db=tmp_path/'journal.db'
    OfflinePaperScenario(db)
    with pytest.raises(PaperReplayBlocked):
        OfflinePaperScenario(db)

def test_live_and_stale_and_pipe_rejected(tmp_path):
    s=OfflinePaperScenario(tmp_path/'journal.db')
    for bad in (payload(live_execution=True),payload(event_time=(T+timedelta(minutes=5)).isoformat()),
                'BX421|BACKTEST_AUTO|BUY'):
        with pytest.raises(SignalRejected):
            s.apply(bad,now=T,synthetic_price=D('100'),quantity=D('1'))

def test_risk_reject_and_no_duplicate_fill(tmp_path):
    s=OfflinePaperScenario(tmp_path/'journal.db',
                           risk_limits=RiskLimits(D('50'),D('50'),D('10')))
    assert s.apply(payload(),now=T,synthetic_price=D('100'),quantity=D('1')).status=='PAPER_REJECTED'
    with pytest.raises(PaperReplayBlocked):
        s.apply(payload(),now=T,synthetic_price=D('100'),quantity=D('1'))
    assert not s.broker.fills

def test_cfd_profile_denied(tmp_path):
    with pytest.raises(ValueError):
        OfflinePaperScenario(tmp_path/'j.db',policy=IntakePolicy(allowed_markets=frozenset({'CFD'})))

def test_nonfinite_price_denied(tmp_path):
    s=OfflinePaperScenario(tmp_path/'j.db')
    with pytest.raises(ValueError):
        s.apply(payload(),now=T,synthetic_price=D('NaN'),quantity=D('1'))

def test_equity_loss_cancels_paper_pending():
    r=RiskManager(RiskLimits(D('1000'),D('2000'),D('50')))
    b=PaperBroker(r)
    b.queue_paper('evt',OrderRequest('BTCUSDT',Side.BUY,D('1')),D('100'))
    g=PaperEquityGuard(r,D('1000'),max_drawdown_fraction=D('0.5'))
    assert g.observe(T,D('1000'))
    assert not g.observe(T+timedelta(minutes=1),D('950'))
    assert r.halted and not b.pending

def test_peak_drawdown_sticky():
    r=RiskManager(RiskLimits(D('1000'),D('2000'),D('999')))
    g=PaperEquityGuard(r,D('1000'),max_drawdown_fraction=D('0.1'))
    g.observe(T,D('1100'))
    assert not g.observe(T+timedelta(minutes=1),D('989'))
    assert not g.observe(T+timedelta(days=1),D('1030'))

def test_day_baseline_utc_reset():
    r=RiskManager(RiskLimits(D('1000'),D('2000'),D('50')))
    g=PaperEquityGuard(r,D('1000'),max_drawdown_fraction=D('0.9'))
    g.observe(T,D('1000'))
    assert g.observe(T+timedelta(hours=23),D('970'))
    assert g.observe(T+timedelta(days=1),D('970'))
    assert not g.observe(T+timedelta(days=1,minutes=1),D('919'))

@pytest.mark.parametrize('bad',[D('NaN'),D('Infinity'),D('-1')])
def test_nonfinite_equity_fail_closed(bad):
    r=RiskManager(RiskLimits(D('1000'),D('2000'),D('50')))
    g=PaperEquityGuard(r,D('1000'),max_drawdown_fraction=D('0.2'))
    with pytest.raises(ValueError): g.observe(T,bad)
    assert r.halted
