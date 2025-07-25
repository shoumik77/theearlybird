from pydantic import BaseModel
from datetime import date
from typing import Optional, List

class ProductBase(BaseModel):
    name: str
    description: str
    url: str
    launch_date: date
    auto_tags: Optional[List[str]] = None

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int

    class Config:
        orm_mode = True
