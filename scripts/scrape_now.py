from __future__ import annotations
from app.core.config import APP_CITY, POSTAL_CODE, LOCALE, STORE_QUERIES
from app.db.database import SessionLocal
from app.db.crud import upsert_offers
from app.scraper.pipeline import scrape_offers

if __name__ == "__main__":
    offers = scrape_offers(
        city=APP_CITY,
        postal_code=POSTAL_CODE,
        locale=LOCALE,
        store_queries=STORE_QUERIES,
        max_items_per_store=250,
        sleep_s=0.15,
    )

    store_queries = [
    "Walmart",
    "Save-On-Foods",
    "Thrifty Foods",
    "Fairway Market",
    "Country Grocer",
    "Wholesale Club",
    "Quality Foods",
    "Root Cellar",
    "Costco",
    ]
    
    db = SessionLocal()
    try:
        inserted = upsert_offers(db, offers)
    finally:
        db.close()

    print(f"Scrape done. offers={len(offers)} inserted={inserted}")
