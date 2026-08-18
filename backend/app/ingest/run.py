import logging
from app.db.sessions import session_factory
from app.db.models import ScanRun

from datetime import datetime, timezone

logger = logging.getLogger(__name__)

def start_run(source, query):

    with session_factory() as session:

        scan_run = ScanRun(source=source, query=query, started_at=datetime.now(timezone.utc))

        session.add(scan_run)
        session.flush()
        run_id = scan_run.id
        session.commit()

        return run_id

def finish_run(run_id, found, new, changed):
    with session_factory() as session:
    
        scan_run = session.get(ScanRun, run_id)

        if scan_run is None:
            logger.warning(f"{run_id} not found; run left unfinished")
            return

        scan_run.listings_found = found
        scan_run.new_listings = new
        scan_run.changed_listings = changed
        scan_run.finished_at = datetime.now(timezone.utc)

        session.commit()


def fail_run(run_id, exception):
    with session_factory() as session:

        scan_run = session.get(ScanRun, run_id)

        if scan_run is None:
            logger.warning(f"{run_id} not found; unrecorded failure {type(exception).__name__}: {exception}")
            return
        
        scan_run.error_type = type(exception).__name__
        scan_run.error_message = str(exception)
        scan_run.finished_at = datetime.now(timezone.utc)

        session.commit()