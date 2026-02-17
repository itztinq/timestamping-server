from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class TimestampResponse(BaseModel):
    id: int
    filename: str
    file_hash: str
    signature: str
    timestamp: datetime
    user_id: int

    class Config:
        from_attributes = True

class VerifyRequest(BaseModel):
    file_hash: str

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    role: str
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None