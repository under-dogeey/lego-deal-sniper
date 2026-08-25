import pytest, json
from pathlib import Path
from app.matcher.cascade import match
from app.matcher.contract import Outcome

CLAIMS = [Outcome.IDENTIFIED, Outcome.MULTI_SET, Outcome.BULK_LOT]

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

    if result.outcome in CLAIMS:
            assert result.outcome == Outcome(case["expected"]["outcome"])

def test_scoreboard():
    fixtures = load_fixtures()

    claim_outcome_count = 0
    correct_claim_outcome_count = 0

    right_identified = 0
    identified_claims = 0

    dangerous = 0

    for fixture in fixtures:

        result = match(fixture["title"], fixture["description_snippet"], fixture["structured_fields"])
        label = Outcome(fixture["expected"]["outcome"])

        if label in CLAIMS:
            claim_outcome_count += 1
            if result.outcome == label:
                correct_claim_outcome_count += 1
            
        if result.outcome == Outcome.IDENTIFIED:
            identified_claims += 1 
            
            if result.outcome == label:
                right_identified += 1

        if result.outcome in CLAIMS and result.outcome != label and result.confidence >= 0.9:
                dangerous += 1

        


    coverage = (correct_claim_outcome_count / claim_outcome_count) * 100

    print(f"coverage: {coverage:.2f}%")

    if identified_claims > 0:
        precision_on_identified = (right_identified / identified_claims)
        assert precision_on_identified >= 0.95

    else:
        print("no claims yet")

    assert dangerous == 0
