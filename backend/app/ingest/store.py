import logging
from app.db.sessions import session_factory
from app.db.models import RawListing, RawListingPriceHistory
from app.ingest.transform import to_raw_listing
from app.ingest.run import start_run, finish_run, fail_run
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert


PRESERVE_ON_CONFLICT = {"id", "first_seen", "alerted_at", "ended_at", "distance_miles"}

logger = logging.getLogger(__name__)

def to_dict(obj):
    return {c.name: getattr(obj, c.name) for c in RawListing.__table__.columns if c.name != "id"}

def upsert_listings(listings, session):

    if not listings:
        return {}

    rows = [to_dict(listing) for listing in listings]

    stmt = insert(RawListing).values(rows)
    upsert_stmt = stmt.on_conflict_do_update(index_elements=["source", "source_listing_id"], set_=
        {c.name: stmt.excluded[c.name] for c in RawListing.__table__.columns if c.name not in PRESERVE_ON_CONFLICT}).returning(RawListing.id, RawListing.source_listing_id)


    returned_rows = session.execute(upsert_stmt).all()

    ids_by_source_id = {}

    for row in returned_rows:
        ids_by_source_id[row.source_listing_id] = row.id

    return ids_by_source_id

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

    total_new = total_unchanged = total_changed = 0

    for queries in query_strings.values():
        for query in queries:

            run_id = None
            try:
                run_id = start_run("ebay", query)

                summaries = ebay_client.search(query).get("itemSummaries", [])

                listings = [to_raw_listing(s) for s in summaries]
                    
                if not listings:
                    finish_run(run_id, 0, 0, 0)
                    continue

                with session_factory() as session:

                    new, unchanged, changed = store_listings(listings, session)
                    
                    session.commit()

                    total_new += new
                    total_unchanged += unchanged
                    total_changed += changed

                found = len(listings)
                finish_run(run_id, found, new, changed)

            except Exception as e:
                logger.exception(f"query failed: {query}")
                if run_id is not None:
                    fail_run(run_id, e)
                continue

    
    logger.info(f"{total_new} new, {total_unchanged} unchanged, {total_changed} changed")

def write_history(listings, ids, observed_at, session):

    if not listings:
        return 0

    history_rows = []

    for listing in listings:
        history_row = {
            "listing_id": ids[listing.source_listing_id],
            "price": listing.price,
            "observed_at": observed_at
        }
        history_rows.append(history_row)

    stmt = insert(RawListingPriceHistory).values(history_rows)
    session.execute(stmt)

    return len(history_rows)


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

    listings_to_record = new_listings + changed_listings
    now =  datetime.now(timezone.utc)
    write_history( listings_to_record, ids, now, session)

    return (len(new_listings), len(unchanged_listings), len(changed_listings))
