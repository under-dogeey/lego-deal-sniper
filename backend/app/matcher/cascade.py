from app.matcher.contract import Outcome, Method, MatchResult

def match(title, description=None, structured_fields=None) -> MatchResult:

    outcome = Outcome.NOT_LEGO
    method = None
    confidence = 0.0
    signals = {}

    title = title.lower()
    structured_fields = structured_fields or {}
    category = structured_fields.get("category_id")
    signals = {}

    if any(kw in title for kw in ("compatible", "for lego")):
        outcome = Outcome.NOT_LEGO
        confidence = 0.9
        method = Method.STRUCTURED_FIELD
        signals = {"keyword": "compatible"}

    elif category == "171135":
        outcome = Outcome.NOT_LEGO
        confidence = 0.9
        method = Method.STRUCTURED_FIELD
        signals = {"category": "171135"}

    elif any(kw in title for kw in ("mega bloks", "mega blocks"))  and category in ("258040", "258041"):
        outcome = Outcome.NOT_LEGO
        confidence = 0.9
        method = Method.STRUCTURED_FIELD
        signals = {"keyword": "mega bloks", "category": "258040"}

    elif category == "183448":
        outcome = Outcome.BULK_LOT
        confidence = 0.9
        method = Method.STRUCTURED_FIELD
        signals = {"category": "183448"}

    result = MatchResult(outcome=outcome, set_ids=[], alternatives=[], method=method, confidence=confidence, signals=signals)

    return result