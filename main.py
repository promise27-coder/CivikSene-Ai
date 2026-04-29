import re
from pathlib import Path
from shutil import copyfileobj
from uuid import uuid4

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from database.database import Base, SessionLocal, engine
from models.complaint import Complaint
from services.classifier import classify_complaint, classify_priority
from services.notifier import send_high_priority_alert

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_ROOT = BASE_DIR / "uploads"
COMPLAINT_UPLOAD_DIR = UPLOAD_ROOT / "complaints"
ALLOWED_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}

COMPLAINT_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_ROOT)), name="uploads")

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_complaint_record(
    db: Session,
    description: str,
    lat: float | None = None,
    long: float | None = None,
    image_path: str | None = None,
):
    complaint = Complaint(
        description=description,
        category=classify_complaint(description),
        priority=classify_priority(description),
        lat=lat,
        long=long,
        image_path=image_path,
    )

    db.add(complaint)
    db.commit()
    db.refresh(complaint)

    alert_result = send_high_priority_alert(complaint)
    if complaint.priority == "High":
        print(alert_result.message)

    return complaint


def save_complaint_image(image: UploadFile | None) -> str | None:
    if image is None or not image.filename:
        return None

    if image.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="Only image files are allowed")

    original_name = Path(image.filename).name
    original_stem = Path(original_name).stem
    safe_stem = re.sub(r"[^a-zA-Z0-9_-]+", "_", original_stem).strip("_")
    safe_stem = safe_stem or "complaint"
    suffix = ALLOWED_IMAGE_TYPES[image.content_type]
    file_name = f"{uuid4().hex}_{safe_stem}{suffix}"
    file_path = COMPLAINT_UPLOAD_DIR / file_name

    with file_path.open("wb") as buffer:
        copyfileobj(image.file, buffer)

    return f"/uploads/complaints/{file_name}"


@app.get("/")
def home():
    return {"message": "CivicSense AI Running"}


@app.post("/complaints")
def create_complaint(data: dict, db: Session = Depends(get_db)):
    description = data["description"]

    return create_complaint_record(
        db=db,
        description=description,
        lat=data.get("lat"),
        long=data.get("long"),
    )


@app.post("/complaints/upload")
def create_complaint_with_image(
    description: str = Form(...),
    lat: float | None = Form(None),
    long: float | None = Form(None),
    image: UploadFile | None = File(None),
    db: Session = Depends(get_db),
):
    image_path = save_complaint_image(image)

    return create_complaint_record(
        db=db,
        description=description,
        lat=lat,
        long=long,
        image_path=image_path,
    )
