"""Independent paper-only equity risk observer; not wired to live execution."""
from datetime import datetime,timezone
from decimal import Decimal
from .risk import RiskManager

class PaperEquityGuard:
    def __init__(self,risk: RiskManager,starting_equity: Decimal,*,
                 max_drawdown_fraction: Decimal):
        if not isinstance(starting_equity,Decimal) or not starting_equity.is_finite() or starting_equity<=0:
            raise ValueError('invalid initial equity')
        if (not isinstance(max_drawdown_fraction,Decimal) or not max_drawdown_fraction.is_finite()
                or not Decimal('0')<max_drawdown_fraction<Decimal('1')):
            raise ValueError('invalid drawdown threshold')
        self.risk=risk
        self.peak=starting_equity
        self.day=None
        self.day_open=starting_equity
        self.last_time=None
        self.limit=max_drawdown_fraction

    def observe(self,when: datetime,equity: Decimal)->bool:
        if when.tzinfo is None or when.utcoffset() is None or not isinstance(equity,Decimal) or not equity.is_finite() or equity<0:
            self.risk.activate_kill_switch()
            raise ValueError('invalid timestamp or equity')
        now=when.astimezone(timezone.utc)
        if self.last_time is not None and now<=self.last_time:
            self.risk.activate_kill_switch()
            raise ValueError('stale equity observation')
        if now.date()!=self.day:
            self.day=now.date()
            self.day_open=equity # first observation, not midnight valuation
        self.last_time=now
        self.peak=max(self.peak,equity)
        if (self.day_open-equity>=self.risk.limits.max_daily_loss or
            (self.peak-equity)/self.peak>=self.limit):
            self.risk.activate_kill_switch()
        return not self.risk.halted
