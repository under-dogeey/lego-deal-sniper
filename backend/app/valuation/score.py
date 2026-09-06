from dataclasses import dataclass
from app.valuation.contract import ConditionBucket

DEAL_THRESHOLD = 0.8

@dataclass(frozen=True)
class Deal:

    set_id: int
    listing_id: int
    bucket: ConditionBucket
    price: float
    landed_cost: float
    low: float
    estimate: float
    n: int | None
    source: str
    name: str
    url: str

    @property
    def ratio(self) -> float:
        return self.landed_cost / self.low

    def __post_init__(self):

        if not (0 < self.low <= self.estimate):
            raise ValueError("estimate and low should be greater than 0; estimate should be greater than low")
        
        if (self.source == "comps") != (self.n is not None):
                raise ValueError("source must be comps; n must be present")
        
        if self.landed_cost <= 0:
             raise ValueError("landed cost cannot be 0 or negative")
        
def score(listing_id, price, url, name, landed, value, threshold=DEAL_THRESHOLD) -> Deal | None: 
     
     if value is None or landed is None:
          return None
     
     ratio = landed / value.low

     if ratio > threshold:
          return None
     
     return Deal(
        set_id = value.set_id, 
        listing_id = listing_id, 
        bucket = value.bucket,
        price = price,
        landed_cost = landed,
        low = value.low,
        estimate = value.estimate,
        n = value.n,
        source = value.source,
        name = name,
        url = url
     )