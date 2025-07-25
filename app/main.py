# app/main.py

from fastapi import FastAPI, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from typing import List, Optional
from datetime import date
from collections import defaultdict

from app import models, schemas, crud, scraper
from app.database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Refresh feed from RSS
@app.post("/refresh-feed")
def refresh_feed(db: Session = Depends(get_db)):
    scraper.sync_new_products(db)
    return {"message": "Feed refreshed successfully"}

# Get filtered products
@app.get("/products", response_model=List[schemas.Product])
def get_products(
    query: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    q = db.query(models.Product)

    # Full-text search
    if query:
        q = q.filter(
            or_(
                models.Product.name.ilike(f"%{query}%"),
                models.Product.description.ilike(f"%{query}%")
            )
        )

    # Tag filter (PostgreSQL array column)
    if tag:
        q = q.filter(models.Product.auto_tags.any(tag))

    # Date filter
    if start_date and end_date:
        q = q.filter(
            and_(
                models.Product.launch_date >= start_date,
                models.Product.launch_date <= end_date
            )
        )

    # Ordering + pagination
    return q.order_by(models.Product.launch_date.desc()).offset(offset).limit(limit).all()

# Trends endpoint for tag frequency over time
@app.get("/trends")
def get_trends(
    interval: str = Query("month", enum=["month", "week"]),
    db: Session = Depends(get_db)
):
    products = db.query(models.Product).all()
    trend_data = defaultdict(lambda: defaultdict(int))

    for p in products:
        if not p.auto_tags:
            continue

        if interval == "month":
            bucket = p.launch_date.strftime("%Y-%m")
        elif interval == "week":
            bucket = p.launch_date.strftime("%Y-W%U")
        else:
            raise HTTPException(status_code=400, detail="Invalid interval")

        for tag in p.auto_tags:
            trend_data[tag][bucket] += 1

    return trend_data
