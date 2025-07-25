# app/main.py

from fastapi import FastAPI, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List, Optional
from datetime import date
from app import models, schemas, crud, scraper
from app.database import SessionLocal, engine
from app.crud import get_all_products

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/refresh-feed")
def refresh_feed(db: Session = Depends(get_db)):
    scraper.sync_new_products(db)
    return {"message": "Feed refreshed successfully"}

@app.get("/products", response_model=List[schemas.Product])
def get_products(
    query: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    q = db.query(models.Product)

    if query:
        q = q.filter(
            or_(
                models.Product.name.ilike(f"%{query}%"),
                models.Product.description.ilike(f"%{query}%")
            )
        )

    if start_date and end_date:
        q = q.filter(
            and_(
                models.Product.launch_date >= start_date,
                models.Product.launch_date <= end_date
            )
        )

    return q.order_by(models.Product.launch_date.desc()).offset(offset).limit(limit).all()
