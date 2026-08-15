import logging
from app.ingest.ebay import EbayClient, CAP
from app.ingest.store import fill_raw_listings
from app.ingest.sweep import NEGATIVE_SIGNALS
from apscheduler.schedulers.blocking import BlockingScheduler

from datetime import datetime

logger = logging.getLogger(__name__)


def cycle(client):

    if client.count >= CAP:
        logger.warning(f"skipping, quota exhausted until {client.count_expires_at}")
        return

    fill_raw_listings(client, NEGATIVE_SIGNALS)

if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')

    client = EbayClient()

    scheduler = BlockingScheduler()
    scheduler.add_job(cycle, 'interval', minutes=15, next_run_time=datetime.now(), args=[client])

    try:
        scheduler.start()

    finally:

        client.close()