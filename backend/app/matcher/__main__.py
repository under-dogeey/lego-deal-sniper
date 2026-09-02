from app.db.sessions import session_factory
from app.matcher.store import backfill_matches

def main():
    with session_factory() as s:
        for outcome, count in backfill_matches(s):
            print(outcome, count)


if __name__ == "__main__":
    main()
    