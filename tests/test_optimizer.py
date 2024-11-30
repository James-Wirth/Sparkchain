import pytest
from matching.optimizer import TradeMatcher

@pytest.fixture
def offers():
    return [
        {"energy": 500, "price": 10},
        {"energy": 300, "price": 12},
    ]

@pytest.fixture
def bids():
    return [
        {"energy": 400, "price": 15},
        {"energy": 200, "price": 14},
    ]

def test_optimize_matching(offers, bids):
    matcher = TradeMatcher(offers, bids)
    matched_trades = matcher.optimize_matching()

    assert matched_trades is not None
    assert sum(trade_energy for _, trade_energy in matched_trades.items()) <= 700
