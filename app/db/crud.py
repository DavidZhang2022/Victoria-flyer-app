from __future__ import annotations
from sqlalchemy import select, desc, func
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.db.models import Offer

def upsert_offers(session: Session, offers: list[Offer]) -> int:
    inserted = 0
    for o in offers:
        exists = session.execute(
            select(Offer.id).where(
                Offer.flyer_item_id == o.flyer_item_id,
                Offer.store_query == o.store_query
            ).limit(1)
        ).scalar_one_or_none()
        if exists:
            continue
        session.add(o)
        inserted += 1
    session.commit()
    return inserted

def search_offers(session: Session, q: str, days: int = 14, limit: int = 200) -> list[Offer]:
    cutoff = datetime.utcnow() - timedelta(days=days)
    stmt = (
        select(Offer)
        .where(Offer.fetched_at_utc >= cutoff)
        .where(func.lower(Offer.raw_name).like(f"%{q.lower()}%"))
        .order_by(desc(Offer.unit_price.isnot(None)), desc(Offer.fetched_at_utc))
        .limit(limit)
    )
    return list(session.execute(stmt).scalars())

def cheapest_by_product_key(session: Session, product_key: str, days: int = 14, limit: int = 30) -> list[Offer]:
    cutoff = datetime.utcnow() - timedelta(days=days)
    stmt = (
        select(Offer)
        .where(Offer.fetched_at_utc >= cutoff)
        .where(Offer.product_key == product_key)
        .order_by(Offer.unit_price.asc().nullslast(), Offer.price.asc().nullslast())
        .limit(limit)
    )
    return list(session.execute(stmt).scalars())

def latest_offers(session: Session, days: int = 14, limit: int = 200) -> list[Offer]:
    cutoff = datetime.utcnow() - timedelta(days=days)
    stmt = (
        select(Offer)
        .where(Offer.fetched_at_utc >= cutoff)
        .order_by(desc(Offer.fetched_at_utc))
        .limit(limit)
    )
    return list(session.execute(stmt).scalars())
