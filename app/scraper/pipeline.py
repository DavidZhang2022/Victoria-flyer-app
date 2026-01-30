from __future__ import annotations
from datetime import datetime
from typing import Any, Dict, List
from app.scraper.flipp_client import make_session, search_item_ids, fetch_item
from app.scraper.unit_parser import parse_price_text, parse_quantity_text, compute_unit_price
from app.scraper.normalize import normalize_name
from app.db.models import Offer
from typing import Optional
from typing import List, Optional

def _safe_get(d: Any, path: str, default=None):
    cur = d
    for part in path.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return default
    return cur

from typing import Any, Dict

def extract_fields(item_json: Dict[str, Any]) -> dict:
    # fetch_item 返回 {"item": {...}}
    it = item_json.get("item") or item_json

    raw_name = (it.get("name") or it.get("title") or "").strip()

    # 你的 debug JSON 里 merchant 是字符串："Fairway Markets"
    merchant_name = (it.get("merchant") or "").strip()

    # 价格字段：price_text / pre_price_text / current_price（按优先级取）
    raw_price_text = (it.get("price_text") or it.get("pre_price_text") or it.get("current_price") or "").strip()

    # 数量字段：你的样例里没看到 quantity，但先这样写；后面可根据 JSON 再补
    raw_qty = (it.get("quantity") or it.get("size") or "").strip()

    raw_valid_from = (it.get("valid_from") or it.get("flyer_valid_from") or "").strip()
    raw_valid_to = (it.get("valid_to") or it.get("flyer_valid_to") or "").strip()

    raw_disclaimer = (it.get("disclaimer_text") or it.get("description") or it.get("flyer_disclaimer_text") or "").strip()

    image_url = (it.get("cutout_image_url") or it.get("image_url") or it.get("image") or "").strip()

    return {
        "raw_name": raw_name,
        "merchant_name": merchant_name,
        "raw_price_text": raw_price_text,
        "raw_quantity": raw_qty,
        "raw_valid_from": raw_valid_from,
        "raw_valid_to": raw_valid_to,
        "raw_disclaimer": raw_disclaimer,
        "image_url": image_url,
        # 可选：用于过滤广告块
        "ttm_label": (it.get("ttm_label") or "").strip(),
    }


def build_offer(city: str, postal_code: str, store_query: str, flyer_item_id: str, item_json: Dict[str, Any]) -> Optional[Offer]:
    f = extract_fields(item_json)
        # 过滤：没有价格的直接跳过
    if not f["raw_price_text"]:
        return None

    # 过滤：See It 类（通常无价的入口块）
    if f.get("ttm_label", "").lower() == "see it":
        return None

    if not f["raw_name"]:
        return None
    price, promo_qty, promo_total = parse_price_text(f["raw_price_text"])
    qty_text = f["raw_quantity"] or f["raw_name"]  # ✅ 兜底：从标题里提取规格
    parsed_qty = parse_quantity_text(qty_text)
    unit_price, unit_label = compute_unit_price(price, parsed_qty)

    return Offer(
        city=city,
        postal_code=postal_code,
        store_query=store_query,
        merchant_name=f["merchant_name"],
        flyer_item_id=flyer_item_id,
        raw_name=f["raw_name"],
        raw_price_text=f["raw_price_text"],
        raw_quantity=f["raw_quantity"] or "",
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

def scrape_offers(city: str, postal_code: str, locale: str, store_queries: List[str],
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
            except Exception as e:
                print("ERR", sq, fid, repr(e))
            if sleep_s > 0:
                time.sleep(sleep_s)

    return out