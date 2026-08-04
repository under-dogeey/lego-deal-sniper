import sys
from app.catalog.sync import fill_lego_sets

incremental = "--incremental" in sys.argv
fill_lego_sets(incremental=incremental)