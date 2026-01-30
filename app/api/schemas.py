from __future__ import annotations
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class OfferOut(BaseModel):
    id: int
    city: str
    postal_code: str
    store_query: str
    merchant_name: str
    flyer_item_id: str
    raw_name: str
    raw_price_text: str
    raw_quantity: str
    raw_valid_from: str
    raw_valid_to: str
    image_url: str
    price: Optional[float] = None
    standardized_qty: Optional[float] = None
    standardized_unit: str
    unit_price: Optional[float] = None
    unit_price_label: str
    product_key: str
    fetched_at_utc: datetime

    class Config:
        from_attributes = True
