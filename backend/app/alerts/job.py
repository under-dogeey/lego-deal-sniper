import logging

from app.alerts import discord, ntfy
from app.db.models import RawListing
from app.valuation.deals import find_deals
from app.valuation.score import format_deal
from app.valuation.transform import to_deal_row
from datetime import date, datetime, timezone

CAP = 5

logger = logging.getLogger(__name__)

def send_alerts(session, cap=CAP):

    deals = find_deals(session, date.today())[:cap]
    alert_count = 0

    for deal in deals:
        text = format_deal(deal)
        discord_ok = discord.send_message(text)
        ntfy_ok = ntfy.send_message(text, click_url=deal.url)

        if discord_ok or ntfy_ok:
            now = datetime.now(timezone.utc)
            session.add(to_deal_row(deal, now))
            session.get(RawListing, deal.listing_id).alerted_at = now
            session.commit()
            alert_count += 1

    logger.info(f"{alert_count} alerts sent")