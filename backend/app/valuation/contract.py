from enum import Enum
from dataclasses import dataclass
from datetime import date

class ConditionBucket(Enum):
    PARTS_ONLY = "parts_only"
    INCOMPLETE = "incomplete"
    USED_NO_BOX =  "used_no_box"
    NEW_OPEN_BOX = "new_open_box"
    NEW_SEALED = "new_sealed"
    USED_COMPLETE = "used_complete"
    
CUES = [(ConditionBucket.PARTS_ONLY, ["parts only", "for parts", "parts lot", "pieces only", "bricks only", "bulk"]), (ConditionBucket.INCOMPLETE, ["incomplete", "not complete", "missing", "partial", "some pieces", "as is", "as-is", "unchecked", "unverified"]), (ConditionBucket.USED_NO_BOX, ["no box", "without box", "no instructions", "loose", "built", "assembled", "displayed"]),(ConditionBucket.NEW_OPEN_BOX, ["open box", "sealed bags", "unopened bags", "bags sealed"]), (ConditionBucket.NEW_SEALED, ["sealed", "nib", "misb", "nisb", "brand new", "factory sealed", "unopened", "never opened"]),  (ConditionBucket.USED_COMPLETE, ["complete", "100%", "all pieces", "with box", "w/ box", "cib"])]

@dataclass(frozen=True)
class ValueEstimate:
    set_id: int
    bucket: ConditionBucket
    estimate: float
    low: float
    high: float
    source: str
    n: int | None
    as_of: date

    def __post_init__(self):

        if not (0 < self.low <= self.estimate <= self.high):
            raise ValueError("estimate, low, high should be greater than 0; estimate should be between low and high")
        
        if (self.source == "comps") != (self.n is not None):
                raise ValueError("source must be comps; n must be present")
        
def to_bucket(condition, title) -> ConditionBucket:

    title = title.lower()

    for bucket, words in CUES:
        if any(word in title for word in words):
            return bucket
        
    return ConditionBucket.NEW_SEALED if condition == "New" else ConditionBucket.INCOMPLETE
