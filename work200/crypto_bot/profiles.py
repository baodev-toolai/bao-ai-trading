"""Strict, review-only market profile loader; never enables brokerage execution."""
from dataclasses import dataclass
from pathlib import Path
import json
from typing import Any
from .signal_intake import IntakePolicy


@dataclass(frozen=True)
class MarketProfile:
    name: str
    venue: str
    market: str
    symbol: str
    timeframe: str
    execution_mode: str
    live_execution: bool
    paper_only: bool
    description: str

    @classmethod
    def from_mapping(cls, obj: dict[str, Any]) -> "MarketProfile":
        if not isinstance(obj, dict):
            raise ValueError("profile must be an object")
        expected = set(cls.__dataclass_fields__)
        if set(obj) != expected:
            raise ValueError("unknown or missing profile keys")
        if any(not isinstance(obj[field], str) or not obj[field].strip()
               for field in ("name", "venue", "market", "symbol", "timeframe", "description")):
            raise ValueError("invalid profile text field")
        if obj["execution_mode"] != "SIGNAL_ONLY":
            raise ValueError("execution mode must remain SIGNAL_ONLY")
        if obj["live_execution"] is not False or obj["paper_only"] is not True:
            raise ValueError("paper-only mode required")
        if obj["market"] not in {"SPOT", "CFD"}:
            raise ValueError("unsupported market type")
        if obj["market"] == "SPOT" and not (obj["venue"] == "OKX" and obj["symbol"] == "BTCUSDT"):
            raise ValueError("unapproved spot research profile")
        if obj["market"] == "CFD" and not (obj["venue"] == "EXNESS" and obj["symbol"] == "XAUUSD"):
            raise ValueError("unapproved CFD reference profile")
        return cls(**obj)

    def intake_policy(self) -> IntakePolicy:
        """Build a REVIEW_ONLY allowlist. This is NOT a broker or order adapter."""
        return IntakePolicy(
            allowed_symbols=frozenset({self.symbol}),
            allowed_exchanges=frozenset({self.venue}),
            allowed_markets=frozenset({self.market}),
            allowed_timeframes=frozenset({self.timeframe}),
        )


def load_profile(path: str | Path) -> MarketProfile:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return MarketProfile.from_mapping(data)