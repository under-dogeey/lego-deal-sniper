import pytest, json
from pathlib import Path
from app.matcher.cascade import match
from app.matcher.contract import Outcome

def load_fixtures():
    dir = Path(__file__).parent
    file_path = dir / "fixtures" / "listings.jsonl"

    listings_jsonl = []

    with open(file_path, "r", encoding="utf-8") as file:
        for listing_jsonl in file:
            listings_jsonl.append(json.loads(listing_jsonl))

    return listings_jsonl

@pytest.mark.parametrize("case", load_fixtures())
def test_fixture(case):
    result = match(case["title"], case["description_snippet"], case["structured_fields"])

    if result.outcome in (Outcome.IDENTIFIED, Outcome.MULTI_SET, Outcome.BULK_LOT):
        if result.outcome == Outcome(case["expected"]["outcome"]):
            assert result.outcome == Outcome(case["expected"]["outcome"])