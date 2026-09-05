from datetime import date
import pytest
from app.valuation.contract import ConditionBucket, ValueEstimate, to_bucket
from app.valuation.estimate import estimate, in_production, RETAIL_FRACTIONS

TODAY = date(2026, 9, 4)
CURRENT = {"set_id": 1, "retail_price_us": 100, "launch_date": date(2025, 1, 1), "exit_date": None, "year": 2025}
RETIRED = {"set_id": 2, "retail_price_us": 50, "launch_date": date(2015, 1, 1), "exit_date": date(2017, 1, 1), "year": 2015}

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

def test_retail_branch_applies_bucket_fractions():
    est = estimate(CURRENT, ConditionBucket.USED_COMPLETE, [], TODAY)
    assert est.source == "retail" and est.n is None
    assert est.low == pytest.approx(55)
    assert est.estimate == pytest.approx(65)
    assert est.high == pytest.approx(75)

def test_comps_branch_median_with_haircut():
    est = estimate(RETIRED, ConditionBucket.USED_NO_BOX, [80, 90, 100, 110, 200], TODAY)
    assert est.source == "comps" and est.n == 5
    assert est.estimate == pytest.approx(80)

def test_too_few_comps_returns_none():
    assert estimate(RETIRED, ConditionBucket.USED_NO_BOX, [80, 90], TODAY) is None

def test_no_retail_anchor_returns_none():
    assert estimate({**CURRENT, "retail_price_us": None}, ConditionBucket.NEW_SEALED, [], TODAY) is None


@pytest.mark.parametrize("record, expected", [
    (CURRENT, True),                                                                  
    ({**CURRENT, "launch_date": date(2023, 1, 1), "year": 2023}, False),            
    ({**CURRENT, "exit_date": date(2026, 6, 1)}, False),                             
])
def test_in_production(record, expected):
    assert in_production(record, TODAY) is expected


def test_retail_fractions_are_well_formed():
    for bucket, row in RETAIL_FRACTIONS.items():
        assert len(row) == 3, bucket
        assert 0 < row[0] < row[1] < row[2], bucket
