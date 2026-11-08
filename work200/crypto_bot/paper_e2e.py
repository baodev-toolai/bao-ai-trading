"""OFFLINE synthetic signal -> risk -> paper only; no network or broker API."""
from __future__ import annotations
import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from hashlib import sha256
from pathlib import Path
from typing import Mapping, Any
from .signal_intake import parse_signal, SignalRejected, IntakePolicy
from .risk import RiskLimits, RiskManager
from .paper_broker import PaperBroker
from .models import OrderRequest, Side, Fill

class PaperReplayBlocked(RuntimeError):
    pass

class ReviewInbox:
    """Persist replay IDs; a session cannot restart without portfolio reconciliation."""
    def __init__(self, path: str | Path):
        self.path = Path(path)
        if str(self.path) == ':memory:':
            raise ValueError('file-backed sqlite required')
        self.path.parent.mkdir(parents=True,exist_ok=True)
        with self.connection() as db:
            db.execute("CREATE TABLE IF NOT EXISTS sessions (name TEXT PRIMARY KEY)")
            db.execute("""CREATE TABLE IF NOT EXISTS events
                (id TEXT PRIMARY KEY, digest TEXT NOT NULL,
                 status TEXT NOT NULL CHECK(status IN
                 ('REVIEW_ONLY','PAPER_REJECTED','PAPER_FILLED')))""")

    def connection(self):
        db=sqlite3.connect(str(self.path),timeout=5)
        db.execute('PRAGMA synchronous=FULL')
        return db

    def claim_session(self):
        with self.connection() as db:
            try:
                db.execute("INSERT INTO sessions(name) VALUES('offline')")
            except sqlite3.IntegrityError as exc:
                raise PaperReplayBlocked('restart or concurrent run blocked') from exc

    def reserve(self, event_id: str, payload: Mapping[str,Any]):
        try:
            digest=sha256(json.dumps(payload,sort_keys=True,allow_nan=False,
                       separators=(',',':')).encode('utf8')).hexdigest()
        except (ValueError,TypeError) as exc:
            raise SignalRejected('noncanonical payload') from exc
        with self.connection() as db:
            try:
                db.execute("INSERT INTO events(id,digest,status) VALUES(?,?,?)",
                           (event_id,digest,'REVIEW_ONLY'))
            except sqlite3.IntegrityError as exc:
                raise PaperReplayBlocked('duplicate/replay event_id') from exc

    def finish(self,event_id: str,status: str):
        if status not in ('PAPER_FILLED','PAPER_REJECTED'):
            raise ValueError('invalid terminal state')
        with self.connection() as db:
            changed=db.execute("UPDATE events SET status=? WHERE id=? AND status='REVIEW_ONLY'",
                               (status,event_id)).rowcount
            if changed!=1:
                raise PaperReplayBlocked('journal transition rejected')

    def status(self,event_id: str):
        with self.connection() as db:
            row=db.execute("SELECT status FROM events WHERE id=?",(event_id,)).fetchone()
        return row[0] if row else None

@dataclass(frozen=True)
class ScenarioResult:
    status: str
    fill: Fill | None

class OfflinePaperScenario:
    """Synthetic local-only test harness, not authenticated event processing."""
    def __init__(self, db_path: str | Path, *,
                 starting_cash: Decimal=Decimal('10000'),
                 risk_limits: RiskLimits | None=None,
                 policy: IntakePolicy | None=None,
                 fee_rate: Decimal=Decimal('0.001'),
                 slippage_rate: Decimal=Decimal('0.0005')):
        self.policy=policy or IntakePolicy()
        if (self.policy.allowed_symbols!=frozenset({'BTCUSDT'}) or
            self.policy.allowed_exchanges!=frozenset({'OKX'}) or
            self.policy.allowed_markets!=frozenset({'SPOT'}) or
            self.policy.allowed_timeframes!=frozenset({'15m'})):
            raise ValueError('offline test is BTCUSDT/OKX/SPOT/15m only')
        self.journal=ReviewInbox(db_path)
        self.journal.claim_session() # Never resume an in-memory position state.
        self.risk=RiskManager(risk_limits or RiskLimits(Decimal('1000000'),
                                                     Decimal('1000000'),Decimal('100000')))
        self.broker=PaperBroker(self.risk,starting_cash=starting_cash,
                                fee_rate=fee_rate,slippage_rate=slippage_rate)

    def apply(self,payload: Mapping[str,Any],*,now: datetime,
              synthetic_price: Decimal,quantity: Decimal)->ScenarioResult:
        signal=parse_signal(payload,self.policy,now=now)
        if not isinstance(synthetic_price,Decimal) or not synthetic_price.is_finite() or synthetic_price<=0:
            raise ValueError('synthetic price must be finite positive Decimal')
        order=OrderRequest(signal.symbol,Side(signal.side),quantity)
        self.journal.reserve(signal.event_id,payload)
        try:
            fill=self.broker.submit(order,synthetic_price)
        except PermissionError:
            self.journal.finish(signal.event_id,'PAPER_REJECTED')
            return ScenarioResult('PAPER_REJECTED',None)
        # If process crashes before finish, REVIEW_ONLY stays and restart is blocked.
        self.journal.finish(signal.event_id,'PAPER_FILLED')
        return ScenarioResult('PAPER_FILLED',fill)
