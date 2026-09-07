from sqlalchemy import select

from app.db.models import ListingMatch, RawListing
from app.valuation.catalog import load_set_record
from app.valuation.contract import to_bucket

SALES_TAX_RATE = 0.1
SHIPPING_BASE = 7.0
SHIPPING_PER_KG = 3.5
FLAT_SHIPPING = 15.0 

def landed_cost(listing, record) -> float | None:

    if listing.price is None:
        return None
    
    original_price = float(listing.price)
    shipping_cost = float(listing.shipping_cost) if listing.shipping_cost is not None else None
    
    if shipping_cost is None:
        if record["weight_kg"] is not None:
            shipping_cost = SHIPPING_BASE + SHIPPING_PER_KG * float(record["weight_kg"]) 
        else:
            shipping_cost = FLAT_SHIPPING
    
    tax = float(original_price * SALES_TAX_RATE)

    price = original_price + shipping_cost + tax

    return price

def load_comps(session, set_id, bucket, exclude_listing_id=None) -> list[float]:

    comps = []
    
    stmt = (
        select(RawListing)
        .join(ListingMatch)
        .where(ListingMatch.outcome == "identified")
        .where(ListingMatch.confidence >= 0.9)
        .where(ListingMatch.set_ids.contains([set_id]))
        .where(RawListing.price.is_not(None))
        )
    
    listings = session.scalars(stmt).all()

    record = load_set_record(session, set_id)

    for listing in listings:
        if listing.id == exclude_listing_id:
            continue
        if bucket == to_bucket(listing.condition, listing.title, record["name"]):
            cost = landed_cost(listing, record)
            if cost is not None:
                comps.append(cost) 

    return comps
