from __future__ import annotations
from datetime import datetime
from typing import Any, Dict, List
from app.scraper.flipp_client import make_session, search_item_ids, fetch_item
from app.scraper.unit_parser import parse_price_text, parse_quantity_text, compute_unit_price
from app.scraper.normalize import normalize_name
from app.db.models import Offer

def _safe_get(d: Any, path: str, default=None):
    cur = d
    for part in path.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return default
    return cur

def extract_fields(item: Dict[str, Any]) -> dict:
    raw_name = item.get("name") or item.get("title") or _safe_get(item, "item.name") or _safe_get(item, "item.title") or ""
    merchant_name = _safe_get(item, "merchant.name") or _safe_get(item, "retailer.name") or item.get("merchant_name") or ""
    raw_price_text = item.get("price") or item.get("current_price") or _safe_get(item, "pricing.price") or ""
    if isinstance(raw_price_text, dict):
        raw_price_text = raw_price_text.get("text") or raw_price_text.get("value") or ""
    raw_qty = item.get("quantity") or item.get("size") or _safe_get(item, "display_quantity") or ""
    if isinstance(raw_qty, dict):
        raw_qty = raw_qty.get("text") or raw_qty.get("value") or ""
    raw_valid_from = item.get("valid_from") or item.get("start_date") or _safe_get(item, "flyer.valid_from") or ""
    raw_valid_to = item.get("valid_to") or item.get("end_date") or _safe_get(item, "flyer.valid_to") or ""
    raw_disclaimer = item.get("disclaimer") or item.get("description") or item.get("deal_text") or ""
    image_url = item.get("image_url") or item.get("cutout_image_url") or _safe_get(item, "image.url") or ""
    return {
        "raw_name": str(raw_name).strip(),
        "merchant_name": str(merchant_name).strip(),
        "raw_price_text": str(raw_price_text).strip(),
        "raw_quantity": str(raw_qty).strip(),
        "raw_valid_from": str(raw_valid_from).strip(),
        "raw_valid_to": str(raw_valid_to).strip(),
        "raw_disclaimer": str(raw_disclaimer).strip(),
        "image_url": str(image_url).strip(),
    }

def build_offer(city: str, postal_code: str, store_query: str, flyer_item_id: str, item_json: Dict[str, Any]) -> Offer | None:
    f = extract_fields(item_json)
    if not f["raw_name"]:
        return None
    price, promo_qty, promo_total = parse_price_text(f["raw_price_text"])
    parsed_qty = parse_quantity_text(f["raw_quantity"])
    unit_price, unit_label = compute_unit_price(price, parsed_qty)

    return Offer(
        city=city,
        postal_code=postal_code,
        store_query=store_query,
        merchant_name=f["merchant_name"],
        flyer_item_id=flyer_item_id,
        raw_name=f["raw_name"],
        raw_price_text=f["raw_price_text"],
        raw_quantity=f["raw_quantity"],
        raw_valid_from=f["raw_valid_from"],
        raw_valid_to=f["raw_valid_to"],
        raw_disclaimer=f["raw_disclaimer"],
        image_url=f["image_url"],
        source_item_url=f"https://backflipp.wishabi.com/flipp/items/{flyer_item_id}",
        price=price,
        promo_qty=promo_qty,
        promo_total_price=promo_total,
        standardized_qty=(parsed_qty.qty if parsed_qty else None),
        standardized_unit=(parsed_qty.unit if parsed_qty else ""),
        unit_price=unit_price,
        unit_price_label=(unit_label or ""),
        product_key=normalize_name(f["raw_name"]),
        fetched_at_utc=datetime.utcnow(),
    )

def scrape_offers(city: str, postal_code: str, locale: str, store_queries: list[str],
                  max_items_per_store: int = 250, sleep_s: float = 0.2) -> List[Offer]:
    session = make_session()
    out: List[Offer] = []
    import time
    for sq in store_queries:
        ids = search_item_ids(session, sq, postal_code, locale, limit=max_items_per_store)
        for fid in ids:
            try:
                item = fetch_item(session, fid, locale)
                offer = build_offer(city, postal_code, sq, fid, item)
                if offer:
                    out.append(offer)
            except Exception:
                pass
            if sleep_s > 0:
                time.sleep(sleep_s)
    return out
