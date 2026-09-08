import logging

from sqlalchemy import select

from app.db.models import ListingMatch, RawListing
from app.valuation.catalog import load_set_record
from app.valuation.comps import landed_cost, load_comps
from app.valuation.contract import to_bucket
from app.valuation.estimate import estimate
from app.valuation.pricecharting import load_latest_sample
from app.valuation.score import DEAL_THRESHOLD, Deal, score

logger = logging.getLogger(__name__)

def find_deals(session, today, threshold=DEAL_THRESHOLD) -> list[Deal]:

    deals = []

    stmt = (
        select(RawListing, ListingMatch)
        .join(ListingMatch)
        .where(ListingMatch.outcome == "identified")
        .where(ListingMatch.confidence >= 0.9)
        .where(ListingMatch.method == 'set_number')
        .where(RawListing.price.is_not(None))
        .where(RawListing.alerted_at.is_(None))
        .where(RawListing.raw_json["itemGroupType"].astext.is_ (None))
        .where(RawListing.raw_json["itemLocation"]["country"].astext == "US")
        .where(RawListing.leaf_category_id != "263012")
        )
    
    listings = session.execute(stmt).all()

    for listing, lm in listings:
        try:
            set_id = lm.set_ids[0]
            record = load_set_record(session, set_id)
            if record is None:
                continue

            bucket = to_bucket(listing.condition, listing.title, record["name"])
            comps = load_comps(session, set_id, bucket, exclude_listing_id=listing.id)
            sample = load_latest_sample(session, set_id, bucket)
            value = estimate(record, bucket, comps, today, sample)
            landed = landed_cost(listing, record)
            deal = score(listing_id=listing.id, price=float(listing.price), url=listing.item_web_url, name=record["name"], number=record["number"], landed=landed, value=value, threshold=threshold)

            if deal is not None:
                deals.append(deal)

        except Exception:
            logger.exception(f"error for {listing.id}")
            session.rollback()
            continue

    return deals