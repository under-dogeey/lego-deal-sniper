from app.matcher.cascade import match
from app.matcher.contract import Outcome

def test_stub_returns_not_lego():
    result = match("LEGO Star Wars 75192")
    assert result.outcome == Outcome.NOT_LEGO

def test_stub_makes_no_set_claims():
    result = match("anything")
    assert result.set_ids == []