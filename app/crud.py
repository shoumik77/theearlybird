from sqlalchemy.orm import Session
from app import models, schemas

def create_product(db: Session, product: schemas.ProductCreate):
    db_product = models.Product(
        name=product.name,
        description=product.description,
        url=product.url,
        tags=product.tags,
        launch_date=product.launch_date
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def get_product_by_url(db: Session, url: str):
    return db.query(models.Product).filter(models.Product.url == url).first()

def get_all_products(db: Session):
    return db.query(models.Product).order_by(models.Product.launch_date.desc()).all()

def get_products(db: Session, skip: int = 0, limit: int = 50):
    return db.query(models.Product).offset(skip).limit(limit).all()
