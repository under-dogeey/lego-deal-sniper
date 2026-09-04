import logging

from app.alerts import discord, ntfy
from app.db.models import RawListing, ListingMatch
from app.matcher.contract import Outcome
from sqlalchemy import select
from datetime import datetime, timezone

MAX_PRICE = 25
CAP = 5

logger = logging.getLogger(__name__)

def send_alerts(session, price=MAX_PRICE, cap=CAP):

    stmt = (
        select(RawListing)
        .join(ListingMatch)
        .where(RawListing.price < price)
        .where(RawListing.alerted_at.is_ (None))
        .where(RawListing.raw_json["itemGroupType"].astext.is_ (None))
        .where(ListingMatch.outcome != Outcome.NOT_LEGO.value)
        .where(ListingMatch.confidence >= 0.8)
        .limit(cap)
    )

    listings = session.scalars(stmt).all()

    alert_count = 0

    for listing in listings:
        discord_ok = discord.send(listing)
        ntfy_ok = ntfy.send(listing)

        if discord_ok or ntfy_ok:
            listing.alerted_at = datetime.now(timezone.utc)
            session.commit()
            alert_count += 1
        
    logger.info(f"{alert_count} alerts sent")
        