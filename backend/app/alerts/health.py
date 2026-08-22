import logging
from app.db.sessions import session_factory
from app.db.models import ScanRun
from app.ingest.sweep import NEGATIVE_SIGNALS
from app.alerts import discord, ntfy
from sqlalchemy import select, func

from datetime import timedelta

STALE_LAG_HOURS = 6

logger = logging.getLogger(__name__)

def stale_queries(lag_hours):

    with session_factory() as session:

        last_success_at = dict(session.execute(select(ScanRun.query, func.max(ScanRun.finished_at).filter(ScanRun.error_type.is_(None))).group_by(ScanRun.query)).all())

        newest_success = max((v for v in last_success_at.values() if v is not None), default=None)

        if newest_success is None:
            return []

        cutoff = newest_success - timedelta(hours=lag_hours)

        stale = []

        for queries in NEGATIVE_SIGNALS.values():
            for query in queries:
                if last_success_at.get(query) is None:
                    stale.append(query)
                elif last_success_at.get(query) < cutoff:
                    stale.append(query)

        return stale

def alert_stale_queries(hours=STALE_LAG_HOURS):
    
    queries = stale_queries(hours)

    if not queries:
        logger.info("no stale queries")
        return
    
    negative_signals = []
    
    for signals in NEGATIVE_SIGNALS.values():
        for signal in signals:
            negative_signals.append(signal)

    queries_count = len(queries)
    negative_signals_count = len(negative_signals)

    message = f"{queries_count} of {negative_signals_count} queries stale (>{hours}h): {", ".join(queries)}"
    
    discord_ok = discord.send_message(message)
    ntfy_ok = ntfy.send_message(message)

    if discord_ok or ntfy_ok:
        logger.warning(message)

    else:
        logger.error("stale query alert reached no channels")


