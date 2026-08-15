from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import DateTime, UniqueConstraint, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB, ARRAY


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

class RawListing(Base):
    __tablename__ = "raw_listings"

    __table_args__ = (
        UniqueConstraint(
            "source", "source_listing_id", name="uq_raw_listings_source_listing_id"
        ),
    )

    def __repr__(self) -> str:
        return f"RawListing(source_listing_id={self.source_listing_id!r}, title={self.title[0:40]!r}, price={self.price!r})"

    id: Mapped[int] = mapped_column(primary_key=True)
    source: Mapped[str]
    source_listing_id: Mapped[str]
    title: Mapped[str]
    price: Mapped[Optional[Decimal]]
    currency: Mapped[Optional[str]]
    shipping_cost: Mapped[Optional[Decimal]]
    condition: Mapped[Optional[str]]
    condition_id: Mapped[Optional[str]]
    buying_options: Mapped[list[str]] = mapped_column(ARRAY(String))
    epid: Mapped[Optional[str]]
    leaf_category_id: Mapped[str]
    item_web_url: Mapped[str]
    image_urls: Mapped[list[str]] = mapped_column(ARRAY(String))
    seller_feedback_score: Mapped[Optional[int]]
    seller_feedback_percentage: Mapped[Optional[Decimal]]
    item_creation_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    item_origin_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    bid_count: Mapped[Optional[int]]
    current_bid_price: Mapped[Optional[Decimal]]
    item_end_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    is_pickup_only: Mapped[bool]
    distance_miles: Mapped[Optional[int]]
    first_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    last_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    alerted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    raw_json: Mapped[dict] = mapped_column(JSONB)

class RawListingPriceHistory(Base):
    __tablename__ = "raw_listings_price_history"

    def __repr__(self) -> str:
        return f"RawListingPriceHistory(listing_id={self.listing_id!r}, price={self.price!r}, observed_at={self.observed_at!r})"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    listing_id: Mapped[int] = mapped_column(ForeignKey("raw_listings.id"), index=True)
    price: Mapped[Optional[Decimal]]
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))