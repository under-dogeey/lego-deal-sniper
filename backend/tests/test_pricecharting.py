import csv, pytest
from datetime import date
from decimal import Decimal
from pathlib import Path
from app.valuation.pricecharting import extract_number, parse_csv, resolve_set, to_samples

SAMPLED_AT = date(2026, 9, 6)

FAKE_CATALOG = {
    "75192": [
        {"set_id": 26725, "name": "Millennium Falcon", "theme": "Star Wars", "year": 2017, "match_string": "millennium falcon star wars"},
    ],
    "1969": [
        {"set_id": 111, "name": "Police Station", "theme": "City", "year": 1980, "match_string": "police station city"},
        {"set_id": 222, "name": "Space Cruiser", "theme": "Space", "year": 1979, "match_string": "space cruiser space"},
    ],
}

def load_fixture():
    file_path = Path(__file__).parent / "fixtures" / "pricecharting.csv"

    with open(file_path, encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))
    
@pytest.mark.parametrize(
    "product_name, expected",
    [
        ("Millennium Falcon #75192", "75192"),
        ("C-3PO #4521221", "4521221"),
        ("Detention Block Rescue [Celebration]", None),
    ],
)
def test_extract_number(product_name, expected):
    assert extract_number(product_name) == expected


def test_resolve_unique_number():
    assert resolve_set("75192", "LEGO Star Wars", FAKE_CATALOG) == 26725


def test_resolve_reused_number_tiebreaks_on_theme():
    assert resolve_set("1969", "LEGO City", FAKE_CATALOG) == 111
    assert resolve_set("1969", "LEGO Space", FAKE_CATALOG) == 222


def test_resolve_reused_number_refuses_when_theme_matches_none():
    assert resolve_set("1969", "LEGO Technic", FAKE_CATALOG) is None


def test_resolve_absent_number():
    assert resolve_set("4521221", "LEGO Star Wars", FAKE_CATALOG) is None


def test_resolve_none_number():
    assert resolve_set(None, "LEGO Star Wars", FAKE_CATALOG) is None


def test_to_samples_full_row():
    row = {"id": "12345", "product-name": "Millennium Falcon #75192", "console-name": "LEGO Star Wars",
           "new-price": "700.00", "cib-price": "523.00", "loose-price": "266.00", "sales-volume": "412"}

    samples = to_samples(row, 26725, SAMPLED_AT)

    assert len(samples) == 3
    prices = {s["bucket"]: s["price"] for s in samples}
    assert prices == {
        "new_sealed": Decimal("700.00"),
        "used_complete": Decimal("523.00"),
        "used_no_box": Decimal("266.00"),
    }
    for sample in samples:
        assert sample["set_id"] == 26725
        assert sample["source"] == "pricecharting"
        assert sample["sales_volume"] == 412
        assert sample["pc_id"] == 12345
        assert sample["sampled_at"] == SAMPLED_AT


def test_to_samples_skips_empty_cells():
    row = {"id": "12349", "product-name": "Millennium Falcon #75192", "console-name": "LEGO Star Wars",
           "new-price": "700.00", "cib-price": "523.00", "loose-price": "", "sales-volume": ""}

    samples = to_samples(row, 26725, SAMPLED_AT)

    assert len(samples) == 2
    assert {s["bucket"] for s in samples} == {"new_sealed", "used_complete"}
    assert all(s["sales_volume"] is None for s in samples)


def test_parse_csv_fixture():
    rows = load_fixture()

    samples, count = parse_csv(rows, FAKE_CATALOG, SAMPLED_AT)

    assert count == {"not_lego": 0, "no_number": 1, "unresolved": 1, "joined": 3}
    assert sum(count.values()) == len(rows)
    assert len(samples) == 8


def test_parse_csv_not_lego_row_is_counted_not_parsed():
    rows = [{"id": "1", "product-name": "EarthBound #6910", "console-name": "Super Nintendo",
             "new-price": "530.00", "cib-price": "429.95", "loose-price": "172.44", "sales-volume": "50"}]

    samples, count = parse_csv(rows, FAKE_CATALOG, SAMPLED_AT)

    assert samples == []
    assert count == {"not_lego": 1, "no_number": 0, "unresolved": 0, "joined": 0}