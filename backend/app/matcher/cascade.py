from app.matcher.contract import Outcome, Method, MatchResult
from app.matcher.extract import extract_set_numbers
from rapidfuzz import fuzz

def corroborated(title, record, number) -> bool:
    return fuzz.token_set_ratio(title, record["name"].lower()) >= 60 or record["theme"].lower() in title or len(number) >= 5

def match(title, description=None, structured_fields=None, catalog=None) -> MatchResult:

    outcome = Outcome.NOT_LEGO
    set_ids = []
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

    result = MatchResult(outcome=outcome, set_ids=set_ids, alternatives=[], method=method, confidence=confidence, signals=signals)

    return result