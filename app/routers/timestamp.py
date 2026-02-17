from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, crypto, auth
from ..database import SessionLocal
from datetime import datetime
from ..schemas import TimestampWithUserResponse
from ..limiter import limiter
from ..config import RATE_LIMIT_UPLOAD, RATE_LIMIT_DELETE, RATE_LIMIT_GENERAL
from fastapi import Request

router = APIRouter(prefix="/api/timestamps", tags=["timestamps"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/upload", response_model=schemas.TimestampWithUserResponse)
@limiter.limit(RATE_LIMIT_UPLOAD)
async def upload_document(
    request: Request,
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
        owner = db.query(models.User).filter(models.User.id == existing.user_id).first()
        return TimestampWithUserResponse(
            id=existing.id,
            filename=existing.filename,
            file_hash=existing.file_hash,
            signature=existing.signature,
            timestamp=existing.timestamp,
            user_id=existing.user_id,
            username=owner.username if owner else "unknown"
        )
    
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
    
    return TimestampWithUserResponse(
        id=record.id,
        filename=record.filename,
        file_hash=record.file_hash,
        signature=record.signature,
        timestamp=record.timestamp,
        user_id=record.user_id,
        username=current_user.username
    )

@router.post("/verify")
@limiter.limit(RATE_LIMIT_GENERAL)
async def verify_document(
    request: Request, 
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
    ):
    
    contents = await file.read()
    file_hash = crypto.compute_file_hash(contents)
    
    result = db.query(
        models.TimestampRecord,
        models.User.username
    ).join(
        models.User, models.TimestampRecord.user_id == models.User.id
    ).filter(
        models.TimestampRecord.file_hash == file_hash
    ).first()
    
    if not result:
        raise HTTPException(status_code=404, detail="Document not found in archive")
    
    record, username = result
    is_valid = crypto.verify_signature(record.file_hash, record.timestamp, record.signature)
    
    return {
        "verified": is_valid,
        "original_name": record.filename,
        "record": TimestampWithUserResponse(
            id=record.id,
            filename=record.filename,
            file_hash=record.file_hash,
            signature=record.signature,
            timestamp=record.timestamp,
            user_id=record.user_id,
            username=username
        )
    }

@router.get("/", response_model=List[schemas.TimestampWithUserResponse])
@limiter.limit(RATE_LIMIT_GENERAL)
async def list_timestamps(
    request: Request,
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
    ):

    if current_user.role == "admin":
        records = db.query(
            models.TimestampRecord,
            models.User.username
        ).join(
            models.User, models.TimestampRecord.user_id == models.User.id
        ).offset(skip).limit(limit).all()
        
        return [
            TimestampWithUserResponse(
                id=r.id,
                filename=r.filename,
                file_hash=r.file_hash,
                signature=r.signature,
                timestamp=r.timestamp,
                user_id=r.user_id,
                username=username
            ) for r, username in records
        ]
    else:
        records = db.query(models.TimestampRecord).filter(
            models.TimestampRecord.user_id == current_user.id
        ).offset(skip).limit(limit).all()
        
        return [
            TimestampWithUserResponse(
                id=r.id,
                filename=r.filename,
                file_hash=r.file_hash,
                signature=r.signature,
                timestamp=r.timestamp,
                user_id=r.user_id,
                username=current_user.username
            ) for r in records
        ]

@router.get("/cert")
async def get_certificate():
    with open(crypto.CERTIFICATE_PATH, "rb") as f:
        cert_pem = f.read()
    return {"certificate": cert_pem.decode()}

@router.delete("/{record_id}")
@limiter.limit(RATE_LIMIT_DELETE)
async def delete_timestamp(
    request: Request,
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