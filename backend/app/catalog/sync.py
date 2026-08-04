from app.db.sessions import session_factory
from app.catalog.brickset import BricksetClient
from app.catalog.transform import to_lego_set
from app.db.models import LegoSet
from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert

def to_dict(obj):
    return {c.name: getattr(obj, c.name) for c in LegoSet.__table__.columns}

def _upsert_sets(sets):

    objs = [to_lego_set(s) for s in sets]

    rows = [to_dict(o) for o in objs]

    stmt = insert(LegoSet).values(rows)
    upsert_stmt = stmt.on_conflict_do_update(index_elements=["set_id"], set_=dict({c.name: stmt.excluded[c.name] for c in LegoSet.__table__.columns if c.name != "set_id"}))


    with session_factory() as session:
        session.execute(upsert_stmt)
        session.commit()

    return len(rows)

def fill_lego_sets(incremental=False):

    client = BricksetClient()
    

    if incremental:
        with session_factory() as session:
            watermark = session.scalar(select(func.max(LegoSet.last_updated)))

        sets = client.get_sets(updated_since=watermark.strftime("%Y-%m-%d"))

        if sets:
            count = _upsert_sets(sets)
            print(f"updated {count} sets since {watermark:%Y-%m-%d}")
        else:
            print(f"no changes since {watermark:%Y-%m-%d}")
        
    else:
        years = client.get_years()["years"]
        for y in years:
            sets = client.get_sets(year=y["year"])
            count = _upsert_sets(sets)

            print(y["year"], count)
        
    #print(f"upserted {len(rows)} rows")


    client.close()

