import pytest, json
from pathlib import Path
from app.matcher.cascade import match
from app.matcher.contract import Outcome

CLAIMS = [Outcome.IDENTIFIED, Outcome.MULTI_SET, Outcome.BULK_LOT]
FAKE_CATALOG = {
     "75192": [{'set_id': 26725, 'name': 'Millennium Falcon', 'theme': 'Star Wars', 'year': 2017}],

     "10249": [{'set_id': 24156, 'name': 'Winter Toy Shop', 'theme': 'Creator Expert', 'year': 2015}],

     "41322": [{'set_id': 26760, 'name': 'Snow Resort Ice Rink', 'theme': 'Friends', 'year': 2017}],

     "71007": [{'set_id': 23440, 'name': 'LEGO Minifigures Series 12 {Random bag}', 'theme': 'Collectable Minifigures', 'year': 2014}, {'set_id': 23898, 'name': 'Wizard', 'theme': 'Collectable Minifigures', 'year': 2014}, {'set_id': 23902, 'name': 'Hun Warrior', 'theme': 'Collectable Minifigures', 'year': 2014}, {'set_id': 23906, 'name': 'Fairytale Princess', 'theme': 'Collectable Minifigures', 'year': 2014}, {'set_id': 23891, 'name': 'Video Game Guy', 'theme': 'Collectable Minifigures', 'year': 2014}, {'set_id': 23904, 'name': 'Battle Goddess', 'theme': 'Collectable Minifigures', 'year': 2014}, {'set_id': 23894, 'name': 'Space Miner', 'theme': 'Collectable Minifigures', 'year': 2014}, {'set_id': 23900, 'name': 'Lifeguard', 'theme': 'Collectable Minifigures', 'year': 2014}, {'set_id': 23897, 'name': 'Prospector', 'theme': 'Collectable Minifigures', 'year': 2014}, {'set_id': 23901, 'name': 'Jester', 'theme': 'Collectable Minifigures', 'year': 2014}, {'set_id': 23905, 'name': 'Dino Tracker', 'theme': 'Collectable Minifigures', 'year': 2014}, {'set_id': 23892, 'name': 'Pizza Delivery Man', 'theme': 'Collectable Minifigures', 'year': 2014}, {'set_id': 23896, 'name': 'Rock Star', 'theme': 'Collectable Minifigures', 'year': 2014}, {'set_id': 23895, 'name': 'Swashbuckler', 'theme': 'Collectable Minifigures', 'year': 2014}, {'set_id': 23899, 'name': 'Piggy Guy', 'theme': 'Collectable Minifigures', 'year': 2014}, {'set_id': 23903, 'name': 'Genie Girl', 'theme': 'Collectable Minifigures', 'year': 2014}, {'set_id': 23893, 'name': 'Spooky Girl', 'theme': 'Collectable Minifigures', 'year': 2014}, {'set_id': 23907, 'name': 'LEGO Minifigures - Series 12 - Complete', 'theme': 'Collectable Minifigures', 'year': 2014}, {'set_id': 23908, 'name': 'LEGO Minifigures - Series 12 - Sealed Box', 'theme': 'Collectable Minifigures', 'year': 2014}],

     "60446": [{'set_id': 50910, 'name': 'Galactic Spaceship', 'theme': 'City', 'year': 2025}],

     "60433": [{'set_id': 48387, 'name': 'Modular Space Station', 'theme': 'City', 'year': 2024}],

     "31058": [{'set_id': 26425, 'name': 'Mighty Dinosaurs', 'theme': 'Creator', 'year': 2017}],

     "71700": [{'set_id': 29426, 'name': 'Jungle Raider', 'theme': 'Ninjago', 'year': 2020}]
}

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
    result = match(case["title"], case["description_snippet"], case["structured_fields"], FAKE_CATALOG)

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

        result = match(fixture["title"], fixture["description_snippet"], fixture["structured_fields"], FAKE_CATALOG)
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
        print(f"precision on identified: {precision_on_identified:.2%}")
        assert precision_on_identified >= 0.95
        
    else:
        print("no claims yet")

    assert dangerous == 0

