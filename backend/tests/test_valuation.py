import pytest
from datetime import date
from app.valuation.contract import ConditionBucket, ValueEstimate, to_bucket

@pytest.mark.parametrize("condition, title, expected", [
    ("New","Open box sealed bags", ConditionBucket.NEW_OPEN_BOX),
    ("New", "Incomplete set", ConditionBucket.INCOMPLETE),
    ("Used", "", ConditionBucket.INCOMPLETE),
    ("Used", "complete with box", ConditionBucket.USED_COMPLETE),
    (None, "factory sealed", ConditionBucket.NEW_SEALED),
    ("Used", "Parts only, no minifigs", ConditionBucket.PARTS_ONLY),
    ("Used", "no box, complete", ConditionBucket.USED_NO_BOX),
    ("New", "", ConditionBucket.NEW_SEALED),
])

def test_to_bucket(condition, title, expected):

    assert to_bucket(condition, title) == expected

def test_n_forbidden_on_retail():
    with pytest.raises(ValueError):
        ValueEstimate(1, ConditionBucket.NEW_SEALED, 100, 80, 120, "retail", 5, date.today())

def test_low_above_estimate_rejected():
    with pytest.raises(ValueError):
        ValueEstimate(1, ConditionBucket.NEW_SEALED, 100, 110, 120, "retail", None, date.today())

def test_zero_bound_rejected():
    with pytest.raises(ValueError):
        ValueEstimate(1, ConditionBucket.NEW_SEALED, 100, 0, 120, "retail", None, date.today())
