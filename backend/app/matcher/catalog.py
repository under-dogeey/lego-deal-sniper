from app.db.models import LegoSet
from sqlalchemy import select

def load_catalog(session) -> dict:

    rows = session.execute(select(LegoSet.set_id, LegoSet.number, LegoSet.name, LegoSet.theme, LegoSet.year)).all()

    catalog = {}

    for row in rows:
        catalog.setdefault(row.number, []).append({"set_id": row.set_id, "name": row.name, "theme": row.theme, "year": row.year})

    return catalog