from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List

class TimestampResponse(BaseModel):
    id: int
    filename: str
    file_hash: str
    signature: str
    timestamp: datetime
    user_id: int

    class Config:
        from_attributes = True

class TimestampWithUserResponse(TimestampResponse):
    username: str

class VerifyRequest(BaseModel):
    file_hash: str

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str
    email: EmailStr

class UserResponse(UserBase):
    id: int
    role: str
    created_at: datetime
    email: str
    is_2fa_verified: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None

class OTPRequest(BaseModel):
    code: str

class TempTokenResponse(BaseModel):
    message: str
    temp_token: str

class LoginResponse(BaseModel):
    access_token: Optional[str] = None
    token_type: Optional[str] = None
    requires_2fa: bool
    temp_token: Optional[str] = None
    message: Optional[str] = None