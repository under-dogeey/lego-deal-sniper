import logging
from app.db.models import RawListing, ListingMatch
from app.matcher.catalog import load_catalog
from app.matcher.transform import to_listing_match, to_structured_fields
from app.matcher.cascade import match

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from collections import Counter

logger = logging.getLogger(__name__)

def match_listings(session, listings):
    catalog, pool = load_catalog(session)
    tally = Counter()

    for listing in listings:
        try:
            sf = to_structured_fields(listing.raw_json)
            result = match(listing.title, None, sf, catalog, pool)
            row = to_listing_match(result, listing.id)
            upsert_match(row, session)
            tally[row.outcome] += 1

        except Exception:
            logger.exception(f"listing failed {listing.id}")
            session.rollback()
            continue
        
    session.commit()
    return tally.most_common()

def backfill_matches(session):
    listings = session.execute(select(RawListing)).scalars()
    return match_listings(session, listings)

def match_new_listings(session):
    listings = session.execute(select(RawListing).outerjoin(ListingMatch).where(ListingMatch.id.is_(None))).scalars()
    return match_listings(session, listings)

def upsert_match(row, session):

    values = {c.name: getattr(row, c.name) for c in ListingMatch.__table__.columns if c.name != "id"}
    stmt = insert(ListingMatch).values(values)
    upsert_stmt = stmt.on_conflict_do_update(index_elements=["listing_id"], set_=
        {k: v for k, v in values.items() if k != "listing_id"})
    
    session.execute(upsert_stmt)
