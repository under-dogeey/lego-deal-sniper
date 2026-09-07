from app.db.models import LegoSet


def load_set_record(session, set_id) -> dict | None:

    row = session.get(LegoSet, set_id)

    if row is None:
        return None
    
    return {"number": row.number, "name": row.name, "set_id": row.set_id, "retail_price_us": row.retail_price_us, "launch_date": row.launch_date, "exit_date": row.exit_date, "year": row.year, "weight_kg": row.weight_kg}