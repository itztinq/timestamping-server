from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, crypto, auth
from ..database import SessionLocal
from datetime import datetime

router = APIRouter(prefix="/api/timestamps", tags=["timestamps"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/upload", response_model=schemas.TimestampResponse)
async def upload_document(
    file: UploadFile = File(...), 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    contents = await file.read()
    file_hash = crypto.compute_file_hash(contents)
    
    existing = db.query(models.TimestampRecord).filter(
        models.TimestampRecord.file_hash == file_hash
    ).first()
    if existing:
        return existing
    
    now = datetime.utcnow()
    signature = crypto.sign_hash(file_hash, now)
    
    record = models.TimestampRecord(
        filename=file.filename,
        file_hash=file_hash,
        signature=signature,
        timestamp=now,
        user_id=current_user.id
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    
    return record

@router.post("/verify")
async def verify_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    contents = await file.read()
    file_hash = crypto.compute_file_hash(contents)
    
    record = db.query(models.TimestampRecord).filter(
        models.TimestampRecord.file_hash == file_hash
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="Document not found in archive")
    
    is_valid = crypto.verify_signature(record.file_hash, record.timestamp, record.signature)
    return {
        "verified": is_valid,
        "original_name": record.filename,
        "record": schemas.TimestampResponse.from_orm(record)
    }

@router.get("/", response_model=List[schemas.TimestampResponse])
async def list_timestamps(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    if current_user.role == "admin":
        records = db.query(models.TimestampRecord).offset(skip).limit(limit).all()
    else:
        records = db.query(models.TimestampRecord).filter(
            models.TimestampRecord.user_id == current_user.id
        ).offset(skip).limit(limit).all()
    return records

@router.get("/cert")
async def get_certificate():
    with open(crypto.CERTIFICATE_PATH, "rb") as f:
        cert_pem = f.read()
    return {"certificate": cert_pem.decode()}

@router.delete("/{record_id}")
async def delete_timestamp(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    record = db.query(models.TimestampRecord).filter(models.TimestampRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    
    if current_user.role != "admin" and record.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed to delete this record")
    
    db.delete(record)
    db.commit()
    return {"message": "Record deleted"}