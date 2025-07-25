# app/crud.py

from sqlalchemy.orm import Session
from app import models, schemas

def create_product(db: Session, product: schemas.ProductCreate):
    db_product = models.Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def get_product_by_url(db: Session, url: str):
    return db.query(models.Product).filter(models.Product.url == url).first()

def get_all_products(db: Session, limit: int = 20, offset: int = 0):
    return db.query(models.Product).order_by(models.Product.launch_date.desc()).offset(offset).limit(limit).all()
