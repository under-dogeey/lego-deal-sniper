from app.db.sessions import session_factory
from app.db.models import RawListing
from app.ingest.transform import to_raw_listing
from sqlalchemy.dialects.postgresql import insert

PRESERVE_ON_CONFLICT = {"id", "first_seen", "alerted_at", "ended_at", "distance_miles"}

def to_dict(obj):
    return {c.name: getattr(obj, c.name) for c in RawListing.__table__.columns if c.name != "id"}

def upsert_listings(listings):

    if not listings:
        return 0

    rows = [to_dict(listing) for listing in listings]

    stmt = insert(RawListing).values(rows)
    upsert_stmt = stmt.on_conflict_do_update(index_elements=["source", "source_listing_id"], set_=
        {c.name: stmt.excluded[c.name] for c in RawListing.__table__.columns if c.name not in PRESERVE_ON_CONFLICT})

    with session_factory() as session:
        session.execute(upsert_stmt)
        session.commit()

    return len(rows)

def fill_raw_listings(ebay_client, query_strings):

    total = 0

    for queries in query_strings.values():
        for query in queries:

            summaries = ebay_client.search(query).get("itemSummaries", [])

            listings = [to_raw_listing(s) for s in summaries]
            
            if not listings:
                continue
            
            count = upsert_listings(listings)
            total += count
    
    print(f"upserted {total} rows")
    
