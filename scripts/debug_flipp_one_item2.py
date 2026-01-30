import json
import requests

from app.core.config import POSTAL_CODE, LOCALE
from app.scraper.flipp_client import make_session, search_item_ids, fetch_item

session = make_session()

store_query = "Fairway Market"   # 你也可以换成 "Thrifty Foods" / "Save-On-Foods"
ids = search_item_ids(session=session, store_query=store_query, postal_code=POSTAL_CODE, locale=LOCALE, limit=10)

print("store_query:", store_query)
print("ids_count:", len(ids))
print("first_ids:", ids[:5])

if not ids:
    raise SystemExit("No item ids returned. Check store_query / postal_code / locale.")

item = fetch_item(session=session, flyer_item_id=ids[0], locale=LOCALE)

print("top_keys:", list(item.keys()))
print("item_json_preview:")
print(json.dumps(item, ensure_ascii=False, indent=2)[:4000])
