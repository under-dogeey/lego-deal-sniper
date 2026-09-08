import csv
import logging
import re
from datetime import date, datetime
from zoneinfo import ZoneInfo
from decimal import Decimal
from pathlib import Path

import httpx
from sqlalchemy.dialects.postgresql import insert

from app.core.config import settings
from app.db.models import ValueSample
from app.db.sessions import session_factory
from app.matcher.catalog import load_catalog
from app.valuation.contract import ConditionBucket

logger = logging.getLogger(__name__)

BASE_URL = "https://www.pricecharting.com"
CSV_PATH = "/price-guide/download-custom" 
CSV_ENCODING = "utf-8"
CSV_CATEGORY = "lego-sets"

SOURCE = "pricecharting"
CONSOLE_PREFIX = "LEGO"
NUMBER_PATTERN = re.compile(r"#(\S+)")
CONDITION_MAP = {
    "new-price": ConditionBucket.NEW_SEALED,
    "cib-price": ConditionBucket.USED_COMPLETE,
    "loose-price": ConditionBucket.USED_NO_BOX
}

def download_csv(today, target_dir):

    token = settings.pricecharting_token

    if not token:
        logger.debug("no token found")
        return None
    
    target_dir.mkdir(parents=True, exist_ok=True)

    file_path = target_dir / f"{today}.csv"
    url = BASE_URL + CSV_PATH

    response = httpx.get(url=url, params = {"t": token, "category": CSV_CATEGORY}, timeout=httpx.Timeout(60.0))

    response.raise_for_status()

    file_path.write_bytes(response.content)

    return file_path

def extract_number(product_name: str) -> str | None:

    match = re.search(NUMBER_PATTERN, product_name)

    if not match:
        return None
    
    return match.group(1)

def resolve_set(number: str, console_name: str, catalog: dict) -> int | None:

    records = catalog.get(number, [])
    records_match = []
    theme = console_name.removeprefix("LEGO ")

    if len(records) == 1:
        return records[0]["set_id"]
    
    else:
        for record in records:
            if theme == record["theme"]:
                records_match.append(record)

    if len(records_match) == 1:
        return records_match[0]["set_id"]
    else:
        return None

def to_samples(row: dict, set_id: int, sampled_at: date) -> list[dict]:

    samples = []
    
    for column, bucket in CONDITION_MAP.items():
        if row[column]:
            samples.append({"set_id": set_id, "bucket": bucket.value, "source": SOURCE, "price": Decimal(row[column].removeprefix("$")), "sales_volume": None if row["sales-volume"] == "" else int(row["sales-volume"]), "pc_id": int(row["id"]), "sampled_at": sampled_at})

    return samples

def parse_csv(rows: list[dict], catalog: dict, sampled_at: date) -> tuple[list[dict], dict]:

    samples = []

    count = {
        "not_lego": 0,
        "no_number": 0,
        "unresolved": 0,
        "joined": 0
    }

    for row in rows:
        if not row["console-name"].startswith(CONSOLE_PREFIX):
            count["not_lego"] += 1
            continue

        number = extract_number(row["product-name"])
        if not number:
            count["no_number"] += 1
            continue

        
        set_id = resolve_set(number, row["console-name"], catalog)
        if not set_id:
            count["unresolved"] += 1
            continue

        count["joined"] += 1
        row_samples = to_samples(row, set_id, sampled_at)

        if row_samples:
            samples.extend(row_samples)

    return samples, count


def import_csv(session, path: Path, catalog: dict) -> int:
    
    sampled_at = date.fromisoformat(path.stem)

    with open(path, encoding=CSV_ENCODING, newline="") as file:
        rows = list(csv.DictReader(file))

    samples, counts = parse_csv(rows, catalog, sampled_at)

    if not samples:
        logger.info(f"Samples is empty; Counts: {counts}")
        return 0

    stmt = insert(ValueSample)
    upsert_stmt = stmt.on_conflict_do_nothing(constraint="uq_value_estimates_set_id_bucket_source_sampled_at").returning(ValueSample.id)

    result = session.execute(upsert_stmt, samples).all()
    session.commit()
    rows_inserted = len(result)
    match_rate = counts["joined"] / (counts["joined"] + counts["no_number"] + counts["unresolved"])

    logger.info(f"Rows read: {len(rows)}, Not Lego: {counts["not_lego"]}, No number: {counts["no_number"]}, Unresolved: {counts["unresolved"]}, Joined: {counts["joined"]}, Samples Produced: {len(samples)}, Rows Inserted: {rows_inserted}, Match Rate: {match_rate:.1%}")
        
    return rows_inserted

def pricecharting_cycle():

    try:
        today = datetime.now(ZoneInfo("America/Los_Angeles")).date()

        path = download_csv(today, Path("data/pricecharting"))
        if path is None:
            logger.debug("no pricechartingtoken, skipping download")
            return

        with session_factory() as session:
            catalog, _ = load_catalog(session)
            import_csv(session, path, catalog)

    except Exception:
        logger.exception("pricecharting cycle failed")