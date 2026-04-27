from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from database.database import engine, Base, SessionLocal
from models.complaint import Complaint
from services.classifier import classify_complaint

app = FastAPI()

# 👉 Table auto create
Base.metadata.create_all(bind=engine)

# 👉 DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def home():
    return {"message": "CivicSense AI Running 🚀"}

@app.post("/complaints")
def create_complaint(data: dict, db: Session = Depends(get_db)):
    description = data["description"]

    complaint = Complaint(
        description=description,
        category=classify_complaint(description),
        priority="Normal",
        lat=data.get("lat"),
        long=data.get("long")
    )

    db.add(complaint)
    db.commit()
    db.refresh(complaint)

    return complaint
