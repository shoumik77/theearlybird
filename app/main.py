from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

from app import models, schemas, crud, scraper
from app.database import SessionLocal, engine
from typing import List

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS (optional frontend support)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Refresh feed (sync new Product Hunt posts)
@app.post("/refresh-feed")
def refresh_feed(db: Session = Depends(get_db)):
    scraper.sync_new_products(db)
    return {"message": "Feed refreshed successfully"}

# Get products from DB
@app.get("/products", response_model=List[schemas.Product])
def get_products(db: Session = Depends(get_db)):
    return crud.get_products(db)
