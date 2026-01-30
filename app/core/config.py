from __future__ import annotations
import os
from dotenv import load_dotenv

load_dotenv()

APP_CITY = os.getenv("APP_CITY", "Victoria").strip()
POSTAL_CODE = os.getenv("POSTAL_CODE", "V8W1P6").strip()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./flyers.db").strip()
LOCALE = os.getenv("LOCALE", "en-ca").strip()

STORE_QUERIES = [s.strip() for s in os.getenv(
    "STORE_QUERIES",
    "Walmart,Save-On-Foods,Thrifty Foods,Fairway Market"
).split(",") if s.strip()]
