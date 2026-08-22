from enum import Enum
from dataclasses import dataclass
from typing import Any

class Outcome(Enum):
    IDENTIFIED = "identified"
    MULTI_SET = "multi_set"
    BULK_LOT = "bulk_lot"
    LEGO_UNIDENTIFIED = "lego_unidentified"
    NOT_LEGO = "not_lego"

class Method(Enum):
    STRUCTURED_FIELD = "structured_field"
    BARCODE = "barcode"
    SET_NUMBER = "set_number"
    SET_NUMBER_UNCORROBORATED = "set_number_uncorroborated"
    FUZZY_NAME = "fuzzy_name"
    LLM_TEXT = "llm_text"
    LLM_VISION = "llm_vision"

@dataclass(frozen=True)
class MatchResult:
    outcome: Outcome
    set_ids: list[int]
    alternatives: list[tuple[int, float]]
    method: Method | None
    confidence: float
    signals: dict[str, Any]

    def __post_init__(self):

        if self.outcome == Outcome.IDENTIFIED:
            if not self.set_ids:
                raise ValueError("listing should have a set id")

        if self.outcome in (Outcome.BULK_LOT, Outcome.LEGO_UNIDENTIFIED, Outcome.NOT_LEGO):
            if self.set_ids:
                raise ValueError("listing should not have a set id")

        if self.outcome == Outcome.MULTI_SET:
            if len(self.set_ids) < 2:
                raise ValueError("number of sets must be at least 2")

        if self.confidence < 0 or self.confidence > 1:
            raise ValueError("confidence level must be between 0-1")