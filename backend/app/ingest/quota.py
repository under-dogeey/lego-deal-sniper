from app.db.sessions import session_factory
from app.db.models import ApiCallLog

from sqlalchemy import func, select

def log_call(api, window, now, endpoint):
    
    with session_factory() as session:
    
        row = ApiCallLog(api=api, count_expires_at=window, called_at=now, endpoint=endpoint)

        session.add(row)
        session.commit()

def calls_in_window(api, window) -> int:

    with session_factory() as session:

        read = session.scalar(select(func.count(ApiCallLog.id)).where(ApiCallLog.api == api).where(ApiCallLog.count_expires_at == window))

    return read