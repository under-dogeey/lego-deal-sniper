from app.db.models import ScoredDeal


def to_deal_row(deal, alerted_at) -> ScoredDeal:

    return ScoredDeal(
        listing_id = deal.listing_id,
        set_id = deal.set_id,
        bucket = deal.bucket.value,
        price = deal.price,
        landed_cost = deal.landed_cost,
        low = deal.low,
        estimate = deal.estimate,
        source = deal.source,
        n = deal.n,
        alerted_at = alerted_at
    )