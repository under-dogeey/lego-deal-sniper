from app.ingest.ebay import EbayClient
from app.ingest.store import fill_raw_listings
from app.ingest.sweep import NEGATIVE_SIGNALS
from apscheduler.schedulers.blocking import BlockingScheduler

from datetime import datetime

def cycle(client):

    fill_raw_listings(client, NEGATIVE_SIGNALS)

if __name__ == "__main__":

    client = EbayClient()

    scheduler = BlockingScheduler()
    scheduler.add_job(cycle, 'interval', minutes=15, next_run_time=datetime.now(), args=[client])

    try:
        scheduler.start()

    finally:

        client.close()