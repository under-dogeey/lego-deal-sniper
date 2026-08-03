from app.db.sessions import session_factory
from app.catalog.brickset import BricksetClient
from app.catalog.transform import to_lego_set
from app.db.models import LegoSet
from sqlalchemy.dialects.postgresql import insert

def to_dict(obj):
    return {c.name: getattr(obj, c.name) for c in LegoSet.__table__.columns}

def fill_lego_sets():

    client = BricksetClient()
    sets = client.get_sets(year="1995")
    objs = [to_lego_set(s) for s in sets["sets"]]

    rows = [to_dict(o) for o in objs]

    stmt = insert(LegoSet).values(rows)

    upsert_stmt = stmt.on_conflict_do_update(index_elements=["set_id"], set_=dict({c.name: stmt.excluded[c.name] for c in LegoSet.__table__.columns if c.name != "set_id"}))


    with session_factory() as session:
        session.execute(upsert_stmt)
        session.commit()
        
    print(f"upserted {len(rows)} rows")

    client.close()

if __name__ == "__main__":
    fill_lego_sets()
