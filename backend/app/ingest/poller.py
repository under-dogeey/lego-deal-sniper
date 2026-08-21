import logging, signal
from app.ingest.ebay import EbayClient, CAP
from app.ingest.store import fill_raw_listings
from app.ingest.sweep import NEGATIVE_SIGNALS
from app.alerts.job import send_alerts
from app.db.sessions import session_factory
from apscheduler.schedulers.blocking import BlockingScheduler

from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def stop_scheduler(signum, frame):
    scheduler.shutdown(wait=True)

def alert_cycle():
    with session_factory() as session:
        send_alerts(session)

def cycle(client):

    if client.count >= CAP:
        logger.warning(f"skipping, quota exhausted until {client.count_expires_at}")
        return

    fill_raw_listings(client, NEGATIVE_SIGNALS)

if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')
    logging.getLogger("httpx").setLevel(logging.WARNING)

    client = EbayClient()

    scheduler = BlockingScheduler()
    scheduler.add_job(cycle, 'interval', minutes=15, next_run_time=datetime.now(), args=[client])
    scheduler.add_job(alert_cycle, 'interval', minutes=15, next_run_time=datetime.now() + timedelta(minutes=1))

    signal.signal(signal.SIGTERM, stop_scheduler)

    try:
        scheduler.start()

    finally:      
        client.close()