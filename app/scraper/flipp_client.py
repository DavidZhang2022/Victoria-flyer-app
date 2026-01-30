from __future__ import annotations
import time
import requests
from typing import Any, Dict, List, Optional

BASE = "https://backflipp.wishabi.com/flipp"
SEARCH_URL = f"{BASE}/items/search"
ITEM_URL = f"{BASE}/items"

def make_session() -> requests.Session:
    s = requests.Session()
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36",
        "Accept": "application/json,text/plain,*/*",
        "Accept-Language": "en-CA,en;q=0.9",
    })
    return s

def get_json(session: requests.Session, url: str, params: Optional[Dict[str, Any]] = None,
             timeout: int = 30, retries: int = 3) -> Dict[str, Any]:
    last = None
    for i in range(retries):
        try:
            r = session.get(url, params=params, timeout=timeout)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            last = e
            time.sleep(0.6 * (i + 1))
    raise RuntimeError(f"GET failed: {url} params={params} err={last}")

def search_item_ids(session: requests.Session, store_query: str, postal_code: str, locale: str, limit: int = 300) -> List[str]:
    data = get_json(session, SEARCH_URL, params={"q": store_query, "postal_code": postal_code, "locale": locale})
    items = data.get("items") or []
    ids: List[str] = []
    for it in items[:limit]:
        fid = it.get("flyer_item_id") or it.get("id")
        if fid:
            ids.append(str(fid))
    seen = set()
    out = []
    for x in ids:
        if x not in seen:
            out.append(x)
            seen.add(x)
    return out

def fetch_item(session: requests.Session, flyer_item_id: str, locale: str) -> Dict[str, Any]:
    return get_json(session, f"{ITEM_URL}/{flyer_item_id}", params={"locale": locale})
