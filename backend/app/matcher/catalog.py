from app.db.models import LegoSet
from sqlalchemy import select

def load_catalog(session) -> tuple[dict, list]:

    rows = session.execute(select(LegoSet.set_id, LegoSet.number, LegoSet.name, LegoSet.theme, LegoSet.year, LegoSet.released, LegoSet.category)).all()

    catalog = {}
    pool = []

    for row in rows:
        match_string = (f"{row.name} {row.theme}").lower()

        record = {"set_id": row.set_id, "name": row.name, "theme": row.theme, "year": row.year, "match_string": match_string}
        catalog.setdefault(row.number, []).append(record)

        if row.released and row.category not in ("Gear", "Book"):
            pool.append(record)

    return catalog, pool