from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from .. import models, schemas, auth
from ..database import get_db
import re
from ..limiter import limiter
from ..config import RATE_LIMIT_AUTH
from ..email_service import send_otp_email, generate_otp

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", response_model=schemas.TempTokenResponse)
@limiter.limit(RATE_LIMIT_AUTH)
def register(
        request: Request,
        user: schemas.UserCreate,
        background_tasks: BackgroundTasks,
        db: Session = Depends(get_db)
):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    db_email = db.query(models.User).filter(models.User.email == user.email).first()
    if db_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    if not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[-@$!%*?&_])[A-Za-z\d@$!%*?&_]{8,}$", user.password):
        raise HTTPException(status_code=400,
                            detail="Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, one digit, and one special character (-@$!%*?&_)")

    hashed_password = auth.get_password_hash(user.password)
    role = "admin" if db.query(models.User).count() == 0 else "user"

    new_user = models.User(
        username=user.username,
        password_hash=hashed_password,
        role=role,
        email=user.email,
        is_2fa_verified=False
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    otp_code = generate_otp()
    otp_record = models.OTPCode(
        user_id=new_user.id,
        code=otp_code,
        expires_at=datetime.utcnow() + timedelta(minutes=5)
    )
    db.add(otp_record)
    db.commit()

    send_otp_email(background_tasks, user.email, otp_code)

    temp_token = auth.create_temp_token(new_user.username)

    return {
        "message": "Registration successful. Please check your email for the verification code.",
        "temp_token": temp_token
    }

@router.post("/verify-otp")
def verify_otp(
        otp_request: schemas.OTPRequest,
        request: Request,
        db: Session = Depends(get_db)
):
    token = request.headers.get("X-Temp-Token")
    if not token:
        raise HTTPException(status_code=401, detail="Missing temp token")

    username = auth.verify_temp_token(token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or expired temp token")

    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    otp = db.query(models.OTPCode).filter(
        models.OTPCode.user_id == user.id,
        models.OTPCode.code == otp_request.code,
        models.OTPCode.is_used == False,
        models.OTPCode.expires_at > datetime.utcnow()
    ).first()

    if not otp:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP code")

    otp.is_used = True
    user.is_2fa_verified = True
    db.commit()

    access_token = auth.create_access_token(
        data={"sub": user.username, "role": user.role}
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=schemas.LoginResponse)
@limiter.limit(RATE_LIMIT_AUTH)
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    if not user.is_2fa_verified:
        raise HTTPException(
            status_code=403,
            detail="Account not verified. Please complete the verification process."
        )

    otp_code = generate_otp()
    otp = models.OTPCode(
        user_id=user.id,
        code=otp_code,
        expires_at=datetime.utcnow() + timedelta(minutes=5)
    )
    db.add(otp)
    db.commit()

    send_otp_email(background_tasks, user.email, otp_code)

    temp_token = auth.create_temp_token(user.username)

    return {
        "requires_2fa": True,
        "temp_token": temp_token,
        "message": "Verification code sent to your email."
    }


@router.post("/verify-login")
def verify_login(
        otp_request: schemas.OTPRequest,
        request: Request,
        db: Session = Depends(get_db)
):
    token = request.headers.get("X-Temp-Token")
    if not token:
        raise HTTPException(status_code=401, detail="Missing temp token")

    username = auth.verify_temp_token(token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or expired temp token")

    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    otp = db.query(models.OTPCode).filter(
        models.OTPCode.user_id == user.id,
        models.OTPCode.code == otp_request.code,
        models.OTPCode.is_used == False,
        models.OTPCode.expires_at > datetime.utcnow()
    ).first()

    if not otp:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP code")

    otp.is_used = True
    db.commit()

    access_token = auth.create_access_token(
        data={"sub": user.username, "role": user.role}
    )

    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=schemas.UserResponse)
def read_users_me(current_user: models.User = Depends(auth.get_current_active_user)):
    return current_user