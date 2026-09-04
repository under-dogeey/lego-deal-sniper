from app.matcher.contract import Outcome, Method, MatchResult
from app.matcher.extract import extract_set_numbers
from rapidfuzz import fuzz, process

import re

ALIASES = {
    "millenium": "millennium",
    "tecnic": "technic",
    "harry poter": "harry potter",
    "milennium": "millennium",
}
LOT_PATTERN = re.compile(r"\blot\b")

def corroborated(title, record, number) -> bool:
    return fuzz.token_set_ratio(title, record["name"].lower()) >= 60 or record["theme"].lower() in title or len(number) >= 5

def match(title, description=None, structured_fields=None, catalog=None, pool=None) -> MatchResult:

    outcome = Outcome.NOT_LEGO
    set_ids = []
    alternatives = []
    method = None
    confidence = 0.0
    signals = {}
    candidates = extract_set_numbers(title)

    if candidates:
        signals["extracted_candidates"] = candidates

    
    title = title.lower()

    structured_fields = structured_fields or {}
    catalog = catalog or {}
    valid = [n for n in candidates if n in catalog]
    category = structured_fields.get("category_id")

    hit = next((kw for kw in ("compatible", "for lego") if kw in title), None)

    if hit:
        outcome = Outcome.NOT_LEGO
        confidence = 0.9
        method = Method.STRUCTURED_FIELD
        signals["keyword"] = hit

    elif category == "171135":
        outcome = Outcome.NOT_LEGO
        confidence = 0.9
        method = Method.STRUCTURED_FIELD
        signals["category"] = "171135"

    elif category == "263015":
        outcome = Outcome.NOT_LEGO
        confidence = 0.9
        method = Method.STRUCTURED_FIELD
        signals["category"] = "263015"

    elif any(kw in title for kw in ("mega bloks", "mega blocks"))  and category in ("258040", "258041"):
        outcome = Outcome.NOT_LEGO
        confidence = 0.9
        method = Method.STRUCTURED_FIELD
        signals["keyword"] = "mega bloks"
        signals["category"] = "258040"

    elif category == "183448":
        outcome = Outcome.BULK_LOT
        confidence = 0.9
        method = Method.STRUCTURED_FIELD
        signals["category"] = "183448"

    elif len(valid) >= 2:
        outcome = Outcome.MULTI_SET
        confidence = 0.9
        method = Method.SET_NUMBER
        set_ids = [catalog[n][0]["set_id"] for n in valid]

    elif len(valid) == 1:
        records = catalog[valid[0]]
        best_record = max(records, key=lambda r: fuzz.token_set_ratio(title, r["name"].lower()) )

        if corroborated(title, best_record, valid[0]):
            method = Method.SET_NUMBER
            confidence = 0.95
        else:
            method = Method.SET_NUMBER_UNCORROBORATED
            confidence = 0.55

        outcome = Outcome.IDENTIFIED
        set_ids = [best_record["set_id"]]

    elif pool:
        fuzzy_title = title
        lot_blocked = LOT_PATTERN.search(title)

        for wrong, right in ALIASES.items():
            fuzzy_title = fuzzy_title.replace(wrong, right)

        choices = [r["match_string"] for r in pool]
        results = process.extract(fuzzy_title, choices, scorer=fuzz.token_set_ratio, limit=10)
        top_score = results[0][1]
        leaders = [r for r in results if r[1] == top_score]

        if len(leaders) == 1:
            if top_score >= 75 and top_score - results[1][1] >= 5 and not lot_blocked and fuzz.token_sort_ratio(fuzzy_title, leaders[0][0]) >= 70:
                best_index = leaders[0][2]
                winner = pool[best_index]

                outcome = Outcome.IDENTIFIED
                set_ids = [winner["set_id"]]
                method = Method.FUZZY_NAME
                confidence = 0.8
            
            else:
                for r in leaders:
                    alternatives.append((pool[r[2]]["set_id"], r[1]))
                
        elif len(leaders) > 1:
            judged = sorted(leaders, key=lambda r: fuzz.token_sort_ratio(fuzzy_title, r[0]), reverse=True)
            best_sort = fuzz.token_sort_ratio(fuzzy_title, judged[0][0])
            second_sort = fuzz.token_sort_ratio(fuzzy_title, judged[1][0])

            if best_sort - second_sort >= 10 and best_sort >= 70 and not lot_blocked:
                winner = pool[judged[0][2]]

                outcome = Outcome.IDENTIFIED
                set_ids = [winner["set_id"]]
                method = Method.FUZZY_NAME
                confidence = 0.8

            else:
                for r in leaders:
                    alternatives.append((pool[r[2]]["set_id"], r[1]))

    if method is None and "lego" in title:
        outcome = Outcome.LEGO_UNIDENTIFIED
        confidence = 0.3
        signals["keyword"] = "lego"

    result = MatchResult(outcome=outcome, set_ids=set_ids, alternatives=alternatives, method=method, confidence=confidence, signals=signals)

    return result