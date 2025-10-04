from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base, Session

DATABASE_URL = "sqlite:///./budget.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class BudgetItem(Base):
    __tablename__ = "budget_items"
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, index=True)
    amount = Column(Float)
    currency = Column(String, default="USD")
    type = Column(String)  # "income" or "expense"
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

class BudgetItemIn(BaseModel):
    category: str
    amount: float
    currency: str = "USD"
    type: str = Field(..., pattern="^(income|expense)$")  # ✅ fixed for Pydantic v2
    created_at: Optional[datetime] = None

class BudgetItemOut(BudgetItemIn):
    id: int

    class Config:
        orm_mode = True

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/items/", response_model=BudgetItemOut)
def create_item(item: BudgetItemIn, db: Session = Depends(get_db)):
    db_item = BudgetItem(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.get("/items/", response_model=list[BudgetItemOut])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(BudgetItem).offset(skip).limit(limit).all()

@app.get("/items/{item_id}", response_model=BudgetItemOut)
def read_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(BudgetItem).filter(BudgetItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.delete("/items/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(BudgetItem).filter(BudgetItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
    return {"detail": "Item deleted"}
