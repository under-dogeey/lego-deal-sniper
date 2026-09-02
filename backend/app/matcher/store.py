from app.db.models import RawListing, ListingMatch
from app.matcher.catalog import load_catalog
from app.matcher.transform import to_listing_match, to_structured_fields
from app.matcher.cascade import match

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from collections import Counter

def backfill_matches(session):
    catalog, pool = load_catalog(session)
    listings = session.execute(select(RawListing)).scalars()
    tally = Counter()

    for listing in listings:
        sf = to_structured_fields(listing.raw_json)
        result = match(listing.title, None, sf, catalog, pool)
        row = to_listing_match(result, listing.id)
        upsert_match(row, session)
        tally[row.outcome] += 1
        
    session.commit()

    return tally.most_common()

def upsert_match(row, session):


    values = {c.name: getattr(row, c.name) for c in ListingMatch.__table__.columns if c.name != "id"}
    stmt = insert(ListingMatch).values(values)
    upsert_stmt = stmt.on_conflict_do_update(index_elements=["listing_id"], set_=
        {k: v for k, v in values.items() if k != "listing_id"})
    
    session.execute(upsert_stmt)
