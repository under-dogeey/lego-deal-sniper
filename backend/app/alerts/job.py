import logging

from app.alerts.discord import send
from app.db.models import RawListing
from sqlalchemy import select
from datetime import datetime, timezone

MAX_PRICE = 25
CAP = 5

logger = logging.getLogger(__name__)

def send_alerts(session, price=MAX_PRICE, cap=CAP):

    listings = session.scalars(select(RawListing).where(RawListing.price < price).where(RawListing.alerted_at.is_ (None)).where(RawListing.raw_json["itemGroupType"].astext.is_ (None)).limit(cap)).all()

    alert_count = 0

    for listing in listings:
        if send(listing):
            listing.alerted_at = datetime.now(timezone.utc)
            session.commit()
            alert_count += 1
        
    logger.info(f"{alert_count} alerts sent")
        