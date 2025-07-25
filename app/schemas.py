from pydantic import BaseModel
from datetime import date
from typing import Optional

class ProductBase(BaseModel):
    name: str
    description: str
    url: str
    tags: Optional[str] = None
    launch_date: date

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int

    class Config:
        orm_mode = True
