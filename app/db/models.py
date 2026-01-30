from __future__ import annotations
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Float, DateTime, Integer, Index
from datetime import datetime

class Base(DeclarativeBase):
    pass

class Offer(Base):
    __tablename__ = "offers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    city: Mapped[str] = mapped_column(String(64), index=True)
    postal_code: Mapped[str] = mapped_column(String(16), index=True)

    store_query: Mapped[str] = mapped_column(String(128), index=True)
    merchant_name: Mapped[str] = mapped_column(String(256), default="")

    flyer_item_id: Mapped[str] = mapped_column(String(64), index=True)

    raw_name: Mapped[str] = mapped_column(String(512), index=True)
    raw_price_text: Mapped[str] = mapped_column(String(128), default="")
    raw_quantity: Mapped[str] = mapped_column(String(128), default="")
    raw_valid_from: Mapped[str] = mapped_column(String(64), default="")
    raw_valid_to: Mapped[str] = mapped_column(String(64), default="")
    raw_disclaimer: Mapped[str] = mapped_column(String(1024), default="")
    image_url: Mapped[str] = mapped_column(String(1024), default="")
    source_item_url: Mapped[str] = mapped_column(String(1024), default="")

    price: Mapped[float | None] = mapped_column(Float, nullable=True)
    promo_qty: Mapped[int | None] = mapped_column(Integer, nullable=True)
    promo_total_price: Mapped[float | None] = mapped_column(Float, nullable=True)

    standardized_qty: Mapped[float | None] = mapped_column(Float, nullable=True)
    standardized_unit: Mapped[str] = mapped_column(String(16), default="")
    unit_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    unit_price_label: Mapped[str] = mapped_column(String(16), default="")

    product_key: Mapped[str] = mapped_column(String(512), index=True)

    fetched_at_utc: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index("idx_offer_dedupe", "flyer_item_id", unique=False),
    )
