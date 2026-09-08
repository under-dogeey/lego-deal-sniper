import logging
import statistics
from datetime import date

from app.valuation.contract import ConditionBucket, ValueEstimate

logger = logging.getLogger(__name__)

RETAIL_FRACTIONS = {
    ConditionBucket.NEW_SEALED: (0.85, 0.95, 1.05),
    ConditionBucket.NEW_OPEN_BOX: (0.70, 0.80, 0.90),
    ConditionBucket.USED_COMPLETE:(0.55, 0.65, 0.75),
    ConditionBucket.USED_NO_BOX:  (0.45, 0.55, 0.65),
    ConditionBucket.INCOMPLETE:   (0.12, 0.20, 0.28),
    ConditionBucket.PARTS_ONLY:   (0.05, 0.10, 0.15),
}
MIN_COMPS = 3
PC_MAX_AGE_DAYS = 90
PC_BAND_FRESH = (0.90, 1.10)
PC_BAND_STALE = (0.75, 1.25)
DISAGREEMENT_THRESHOLD = 0.35
COMPS_HAIRCUT = 0.80
IN_PRODUCTION_MONTHS = 36

def in_production(record, today) -> bool:

    if record.get("exit_date") is not None:
        return False
    
    launched = record.get("launch_date") or date(record["year"], 1, 1)
    months = (today.year - launched.year) * 12 + (today.month - launched.month)
    return months <= IN_PRODUCTION_MONTHS

def estimate(record, bucket, comps, today, sample=None) -> ValueEstimate | None:


    if sample and (today - sample["sampled_at"]).days <= PC_MAX_AGE_DAYS:

        if len(comps) >= MIN_COMPS:
            pc = sample["price"]
            median = statistics.median(comps) * COMPS_HAIRCUT

            if abs(pc - median) / median > DISAGREEMENT_THRESHOLD:
                logger.warning(f"set number: {record["number"]}, bucket: {bucket.value}, pc: {pc}, median: {median}, comps count: {len(comps)}")

        return ValueEstimate(set_id=record["set_id"], bucket=bucket, estimate=sample["price"], low=sample["price"]* PC_BAND_FRESH[0], high=sample["price"]* PC_BAND_FRESH[1], source="pricecharting", n=None, as_of=sample["sampled_at"])

    if in_production(record, today):
        retail = record.get("retail_price_us")

        if retail is not None:
            retail = float(retail)
            low_frac, est_frac, high_frac = RETAIL_FRACTIONS[bucket]

            return ValueEstimate(
                set_id=record["set_id"], bucket=bucket,
                estimate=retail * est_frac, low=retail * low_frac, high=retail * high_frac,
                source="retail", n=None, as_of=today,
            )   
    
    elif len(comps) >= MIN_COMPS:
        q25, median, q75 = statistics.quantiles(comps, n=4)
        return ValueEstimate(
            set_id=record["set_id"], bucket=bucket,
            estimate=median * COMPS_HAIRCUT, low=q25 * COMPS_HAIRCUT, high=q75 * COMPS_HAIRCUT,
            source="comps", n=len(comps), as_of=today,
        )

    if sample:
        return ValueEstimate(set_id=record["set_id"], bucket=bucket, estimate=sample["price"], low=sample["price"]* PC_BAND_STALE[0], high=sample["price"]* PC_BAND_STALE[1], source="pricecharting", n=None, as_of=sample["sampled_at"])
            
    return None

    