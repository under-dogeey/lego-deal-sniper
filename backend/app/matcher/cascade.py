from app.matcher.contract import Outcome, MatchResult

def match(title, description=None, structured_fields=None) -> MatchResult:

    outcome = Outcome.NOT_LEGO
    method = None

    result = MatchResult(outcome=outcome, set_ids=[], alternatives=[], method=method, confidence=0.0, signals={})

    return result