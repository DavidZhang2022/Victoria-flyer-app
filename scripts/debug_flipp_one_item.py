import json
from app.scraper.flipp_client import FlippClient
from app.core.config import POSTAL_CODE, LOCALE

client = FlippClient(postal_code=POSTAL_CODE, locale=LOCALE)

# 这里用你已有 store_query 之一（从数据库里能看到 Fairway Market / Thrifty Foods / Save-On-Foods）
store_query = "Fairway Market"

items = client.fetch_items(store_query=store_query)

print("items:", len(items))
print("first keys:", list(items[0].keys()) if items else None)
print("first item preview:")
print(json.dumps(items[0], ensure_ascii=False)[:2000])
