import pytest
from app.matcher.extract import extract_set_numbers

@pytest.mark.parametrize("title, expected", [
    ("LEGO Star Wars UCS Millennium Falcon 75192 7541 Pieces Complete Set Boxed", ["75192"]),
    ("2 Pounds of Legos 31058 71700 unsorted", ["31058", "71700"]),
    ("LEGO Figurine Minifig Star Wars BB-8 Robot Droid Small Photoreceptor SW0661", []),
    ("$1500 obo lego lot", []),
])
def test_extract_set_numbers(title, expected):
    assert(extract_set_numbers(title) == expected)