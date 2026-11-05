"""Profiles never grant order execution or mix CFD reference with spot accounting."""
from pathlib import Path
import json
import pytest
from crypto_bot.profiles import MarketProfile, load_profile

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("file,market,symbol", [
    ("okx_btcusdt_spot_15m.json", "SPOT", "BTCUSDT"),
    ("exness_xauusd_swing_m15.json", "CFD", "XAUUSD"),
])
def test_load_supported_profiles(file, market, symbol):
    p = load_profile(ROOT / "profiles" / file)
    assert p.market == market and p.symbol == symbol
    assert p.live_execution is False and p.paper_only is True
    assert p.intake_policy().allowed_symbols == frozenset({symbol})


def test_rejects_live_toggle():
    d = json.loads((ROOT / "profiles/okx_btcusdt_spot_15m.json").read_text())
    d["live_execution"] = True
    with pytest.raises(ValueError, match="paper-only"):
        MarketProfile.from_mapping(d)


def test_rejects_order_enabled_mode():
    d = json.loads((ROOT / "profiles/okx_btcusdt_spot_15m.json").read_text())
    d["execution_mode"] = "AUTO"
    with pytest.raises(ValueError, match="SIGNAL_ONLY"):
        MarketProfile.from_mapping(d)


def test_rejects_unknown_market():
    d = json.loads((ROOT / "profiles/okx_btcusdt_spot_15m.json").read_text())
    d["market"] = "PERPETUAL"
    with pytest.raises(ValueError, match="unsupported market"):
        MarketProfile.from_mapping(d)


def test_rejects_spot_cross_venue():
    d = json.loads((ROOT / "profiles/okx_btcusdt_spot_15m.json").read_text())
    d["symbol"] = "XAUUSD"
    with pytest.raises(ValueError, match="unapproved"):
        MarketProfile.from_mapping(d)


def test_rejects_unknown_settings():
    d = json.loads((ROOT / "profiles/okx_btcusdt_spot_15m.json").read_text())
    d["api_key"] = "NOT-A-REAL-CREDENTIAL"
    with pytest.raises(ValueError, match="unknown or missing"):
        MarketProfile.from_mapping(d)