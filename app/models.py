from sqlalchemy import Column, Integer, String, Text, Date, DateTime, func, ARRAY
from sqlalchemy.ext.declarative import declarative_base

auto_tags = Column(ARRAY(String))

Base = declarative_base()

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key = True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    url = Column(String(500), nullable=False)
    tags = Column(Text, nullable=True)
    launch_date = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    auto_tags = Column(ARRAY(String)) 
