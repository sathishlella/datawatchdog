import io
import pandas as pd
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models.schemas import Dataset
from app.models.pydantic_models import DatasetOut

router = APIRouter()


@router.get("/", response_model=list[DatasetOut])
def list_datasets(db: Session = Depends(get_db)):
    return db.query(Dataset).order_by(Dataset.created_at.desc()).all()


@router.post("/upload", response_model=DatasetOut)
async def upload_dataset(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(400, "Only CSV files accepted")
    content = await file.read()
    df = pd.read_csv(io.BytesIO(content))
    name = file.filename.replace(".csv", "")
    existing = db.query(Dataset).filter(Dataset.name == name).first()
    if existing:
        db.delete(existing)
        db.commit()
    dataset = Dataset(name=name, columns=list(df.columns), row_count=len(df))
    db.add(dataset)
    db.commit()
    db.refresh(dataset)
    return dataset


@router.delete("/{dataset_id}")
def delete_dataset(dataset_id: int, db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(404, "Dataset not found")
    db.delete(dataset)
    db.commit()
    return {"deleted": dataset_id}
