from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from .database import Base
import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="user")  # 'admin' или 'user'
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    email = Column(String, unique=True, index=True, nullable=False)
    is_2fa_verified = Column(Boolean, default=False)

    timestamps = relationship("TimestampRecord", back_populates="owner")
    otp_codes = relationship("OTPCode", back_populates="owner", cascade="all, delete-orphan")


class TimestampRecord(Base):
    __tablename__ = "timestamps"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    file_hash = Column(String, unique=True, index=True)
    signature = Column(Text)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="timestamps")

class OTPCode(Base):
    __tablename__ = "otp_codes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    code = Column(String(6), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    owner = relationship("User", back_populates="otp_codes")