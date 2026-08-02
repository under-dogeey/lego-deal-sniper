from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import DateTime, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class LegoSet(Base):
    __tablename__ = "lego_sets"

    __table_args__ = (
        UniqueConstraint(
            "number", "number_variant", name="uq_lego_sets_number_variant"
        ),
    )

    def __repr__(self) -> str:
        return f"LegoSet(set_id={self.set_id!r}, number={self.number!r}, name={self.name!r})"

    set_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    number: Mapped[str]
    number_variant: Mapped[int]
    name: Mapped[str]
    year: Mapped[int]
    theme: Mapped[str]
    theme_group: Mapped[Optional[str]]
    subtheme: Mapped[Optional[str]]
    category: Mapped[Optional[str]]
    released: Mapped[bool]
    pieces: Mapped[Optional[int]]
    minifigs: Mapped[Optional[int]]
    launch_date: Mapped[Optional[date]]
    exit_date: Mapped[Optional[date]]
    thumbnail_url: Mapped[Optional[str]]
    image_url: Mapped[Optional[str]]
    owned_by: Mapped[Optional[int]]
    wanted_by: Mapped[Optional[int]]
    retail_price_us: Mapped[Optional[Decimal]]
    rating: Mapped[Optional[Decimal]]
    rating_count: Mapped[Optional[int]]
    weight_kg: Mapped[Optional[Decimal]]
    barcode_ean: Mapped[Optional[str]]
    barcode_upc: Mapped[Optional[str]]
    last_updated: Mapped[datetime] = mapped_column(DateTime(timezone=True))
