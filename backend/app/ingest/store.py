from app.db.sessions import session_factory
from app.db.models import RawListing
from app.ingest.transform import to_raw_listing

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

PRESERVE_ON_CONFLICT = {"id", "first_seen", "alerted_at", "ended_at", "distance_miles"}

def to_dict(obj):
    return {c.name: getattr(obj, c.name) for c in RawListing.__table__.columns if c.name != "id"}

def upsert_listings(listings, session):

    if not listings:
        return 0

    rows = [to_dict(listing) for listing in listings]

    stmt = insert(RawListing).values(rows)
    upsert_stmt = stmt.on_conflict_do_update(index_elements=["source", "source_listing_id"], set_=
        {c.name: stmt.excluded[c.name] for c in RawListing.__table__.columns if c.name not in PRESERVE_ON_CONFLICT}).returning(RawListing.id, RawListing.source_listing_id).all()


    session.execute(upsert_stmt)

    return rows

def fetch_existing_rows(listings, session):

    ids = []
    for listing in listings:
        ids.append(listing.source_listing_id)

    rows = session.execute(select(RawListing.id, RawListing.source_listing_id, RawListing.price).where(RawListing.source == "ebay", RawListing.source_listing_id.in_(ids))).all()

    rows_dict = {}

    for row in rows:
        rows_dict[row.source_listing_id] = (row.id, row.price)

    return rows_dict

def fill_raw_listings(ebay_client, query_strings):

    total = 0

    for queries in query_strings.values():
        for query in queries:

            summaries = ebay_client.search(query).get("itemSummaries", [])

            listings = [to_raw_listing(s) for s in summaries]
            
            if not listings:
                continue
            
            count = upsert_listings(listings)
            total += len(count)
    
    print(f"upserted {total} rows")

def write_history():


def store_listings(listings, session):
    
    existing_listings = fetch_existing_rows(listings, session)

    ids = upsert_listings(listings, session)

    new_listings = []
    changed_listings = []
    unchanged_listings = []

    for listing in listings:
        existing_listing = existing_listings.get(listing.source_listing_id)
        if existing_listing is None:
            new_listings.append(listing)
        else: 
            stored_id, stored_price = existing_listing
            if stored_price == listing.price:
                unchanged_listings.append(listing)
            else:
                changed_listings.append(listing)

    write_history()
