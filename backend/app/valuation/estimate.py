import statistics
from datetime import date

from app.valuation.contract import ConditionBucket, ValueEstimate

RETAIL_FRACTIONS = {
    ConditionBucket.NEW_SEALED: (0.85, 0.95, 1.05),
    ConditionBucket.NEW_OPEN_BOX: (0.70, 0.80, 0.90),
    ConditionBucket.USED_COMPLETE:(0.55, 0.65, 0.75),
    ConditionBucket.USED_NO_BOX:  (0.45, 0.55, 0.65),
    ConditionBucket.INCOMPLETE:   (0.12, 0.20, 0.28),
    ConditionBucket.PARTS_ONLY:   (0.05, 0.10, 0.15),
}
MIN_COMPS = 3
COMPS_HAIRCUT = 0.80
IN_PRODUCTION_MONTHS = 36

def in_production(record, today) -> bool:

    if record.get("exit_date") is not None:
        return False
    
    launched = record.get("launch_date") or date(record["year"], 1, 1)
    months = (today.year - launched.year) * 12 + (today.month - launched.month)
    return months <= IN_PRODUCTION_MONTHS

def estimate(record, bucket, comps, today) -> ValueEstimate | None:

    if in_production(record, today):
        retail = record.get("retail_price_us")
        if retail is None:
            return None
        
        retail = float(retail)
        low_frac, est_frac, high_frac = RETAIL_FRACTIONS[bucket]
        return ValueEstimate(
            set_id=record["set_id"], bucket=bucket,
            estimate=retail * est_frac, low=retail * low_frac, high=retail * high_frac,
            source="retail", n=None, as_of=today,
        )
    
    if len(comps) < MIN_COMPS:
        return None
    q25, median, q75 = statistics.quantiles(comps, n=4)
    return ValueEstimate(
        set_id=record["set_id"], bucket=bucket,
        estimate=median * COMPS_HAIRCUT, low=q25 * COMPS_HAIRCUT, high=q75 * COMPS_HAIRCUT,
        source="comps", n=len(comps), as_of=today,
    )