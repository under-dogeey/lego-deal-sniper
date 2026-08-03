from app.db.sessions import session_factory
from app.catalog.brickset import BricksetClient
from app.catalog.transform import to_lego_set
from app.db.models import LegoSet
from sqlalchemy.dialects.postgresql import insert

#def fill_lego_sets():

    #client = BricksetClient()

    #for set in sets:
        #set = to_lego_set(client.get_sets(year="1995"))
    
    #page_size = 500
    #years = client.get_years()

    #for year in years:
    #    sets = client.get_sets(year=year)
    #    rows = [dict(to_lego_set(s)) for s in sets["sets"]]

        
    #    for set in sets:
    
    #        statement = insert(LegoSet).values(set)

    #        upsert_statement = statement.on_conflict_do_update(#i dont even know anymore)
    #        with session_factory as session:
    #            session.execute(upsert_statement)
    #            session.commit()

if __name__ == "__main__":
    client = BricksetClient()
    sets = client.get_sets(year="1995")
    objs = [to_lego_set(s) for s in sets["sets"]]
    print(len(objs))
    
    print(objs[0])
    print(objs[85])
    print(objs[-1])

    for o in objs:
        if not o.number.isdigit():
            print(o)
    #print(sets["matches"], len(sets["sets"]))
    #print(sets["sets"][0])