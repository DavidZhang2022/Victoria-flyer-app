from __future__ import annotations
import os
import pandas as pd
from app.core.config import APP_CITY, POSTAL_CODE, LOCALE, STORE_QUERIES
from app.scraper.pipeline import scrape_offers

OUT_DIR = "out"
OUT_FILE = os.path.join(OUT_DIR, "victoria_offers.csv")

if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    offers = scrape_offers(APP_CITY, POSTAL_CODE, LOCALE, STORE_QUERIES, max_items_per_store=250, sleep_s=0.1)
    df = pd.DataFrame([{
        "city": o.city,
        "postal_code": o.postal_code,
        "store_query": o.store_query,
        "merchant_name": o.merchant_name,
        "flyer_item_id": o.flyer_item_id,
        "raw_name": o.raw_name,
        "raw_price_text": o.raw_price_text,
        "raw_quantity": o.raw_quantity,
        "raw_valid_from": o.raw_valid_from,
        "raw_valid_to": o.raw_valid_to,
        "price": o.price,
        "unit_price": o.unit_price,
        "unit_price_label": o.unit_price_label,
        "product_key": o.product_key,
        "fetched_at_utc": o.fetched_at_utc.isoformat(),
        "source_item_url": o.source_item_url,
        "image_url": o.image_url,
    } for o in offers])
    df.to_csv(OUT_FILE, index=False, encoding="utf-8-sig")
    print(f"Wrote {OUT_FILE} rows={len(df)}")
