from app.db.models import ListingMatch
from datetime import datetime, timezone

def to_listing_match(result, listing_id) -> ListingMatch:

    return ListingMatch(
        listing_id = listing_id,
        outcome = result.outcome.value,
        method = result.method.value if result.method else None,
        confidence = result.confidence,
        set_ids = result.set_ids,
        alternatives = result.alternatives,
        signals = result.signals,
        matched_at = datetime.now(timezone.utc)
    )

def to_structured_fields(raw_json) -> dict:

    structured_field = {}

    epid = raw_json.get("epid")
    category_id = (raw_json.get("leafCategoryIds") or [None])[0]
    condition = raw_json.get("condition")
    price = raw_json.get("price", {}).get("value")

    if epid is not None:
        structured_field["epid"] = epid

    if category_id is not None:
        structured_field["category_id"] = category_id

    if condition is not None:
        structured_field["condition"] = condition

    if price is not None:
        structured_field["price"] = price

    return structured_field

