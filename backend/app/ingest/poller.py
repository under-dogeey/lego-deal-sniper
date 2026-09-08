import logging, signal, httpx
from app.core.config import settings
from app.ingest.ebay import EbayClient, CAP
from app.ingest.store import fill_raw_listings
from app.ingest.sweep import NEGATIVE_SIGNALS
from app.matcher.store import match_new_listings
from app.valuation.pricecharting import pricecharting_cycle
from app.alerts.job import send_alerts
from app.alerts.health import alert_stale_queries
from app.db.sessions import session_factory
from apscheduler.schedulers.blocking import BlockingScheduler

from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def stop_scheduler(signum, frame):
    scheduler.shutdown(wait=True)

def alert_cycle():
    with session_factory() as session:
        send_alerts(session)

def match_cycle():
    with session_factory() as session:
        tally = match_new_listings(session)
        logger.info(f"matched new listings: {tally}")

def cycle(client):

    if client.count >= CAP:
        logger.warning(f"skipping, quota exhausted until {client.count_expires_at}")
        return

    fill_raw_listings(client, NEGATIVE_SIGNALS)

    health_checks_url = settings.health_checks_url

    if not health_checks_url:
        logger.debug("health check ping failed: invalid health checks url")
        return
    
    try:
        response = httpx.get(health_checks_url)
        response.raise_for_status()

    except Exception:
        logger.warning("health check ping failed")

if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')
    logging.getLogger("httpx").setLevel(logging.WARNING)

    client = EbayClient()

    scheduler = BlockingScheduler()
    scheduler.add_job(cycle, 'interval', minutes=15, next_run_time=datetime.now(), args=[client])
    scheduler.add_job(alert_cycle, 'interval', minutes=15, next_run_time=datetime.now() + timedelta(minutes=2))
    scheduler.add_job(alert_stale_queries, 'cron', hour=19, minute=0)
    scheduler.add_job(match_cycle, 'interval', minutes=15, next_run_time=datetime.now() + timedelta(minutes=1))
    scheduler.add_job(pricecharting_cycle, 'cron', hour="10",timezone="America/Los_Angeles")

    signal.signal(signal.SIGTERM, stop_scheduler)

    try:
        scheduler.start()

    finally:      
        client.close()