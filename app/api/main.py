from __future__ import annotations
from typing import List
from fastapi import FastAPI, Depends, Query
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db import crud
from app.api.schemas import OfferOut

app = FastAPI(title="Victoria Flyer Compare API")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/offers/latest", response_model=List[OfferOut])
def latest(days: int = 14, limit: int = 200, db: Session = Depends(get_db)):
    return crud.latest_offers(db, days=days, limit=limit)

@app.get("/offers/search", response_model=List[OfferOut])
def search(q: str = Query(..., min_length=1), days: int = 14, limit: int = 200, db: Session = Depends(get_db)):
    return crud.search_offers(db, q=q, days=days, limit=limit)

@app.get("/offers/by_product_key", response_model=List[OfferOut])
def by_product_key(product_key: str, days: int = 14, limit: int = 50, db: Session = Depends(get_db)):
    return crud.cheapest_by_product_key(db, product_key=product_key, days=days, limit=limit)
