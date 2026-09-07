import logging
import sys
from pathlib import Path

from app.db.sessions import session_factory
from app.matcher.catalog import load_catalog
from app.valuation.pricecharting import import_csv

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO)

def main():
    path = Path(sys.argv[1])

    with session_factory() as session:
        catalog, _ = load_catalog(session)
        print(import_csv(session, path, catalog))

if __name__ == "__main__":
    main()