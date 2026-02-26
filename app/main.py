from fastapi import FastAPI
from contextlib import asynccontextmanager
from .database import SessionLocal, engine
from . import models, auth, crypto
from .config import (
    ADMIN_USERNAME,
    ADMIN_PASSWORD,
    RATE_LIMIT_GENERAL,
)
from .routers import timestamp, auth as auth_router
import datetime
import logging
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from .limiter import limiter
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    models.Base.metadata.create_all(bind=engine)
    logger.info("Database tables created/verified.")

    db = SessionLocal()
    try:
        user_count = db.query(models.User).count()
        if user_count == 0:
            logger.info("Seeding with initial data...")

            hashed_admin = auth.get_password_hash(ADMIN_PASSWORD)
            admin = models.User(
                username=ADMIN_USERNAME,
                password_hash=hashed_admin,
                role="admin",
                email="admin@example.com",  # додадено
                is_2fa_verified=True  # за да не го попречува тестирањето (може да се смени)
            )
            db.add(admin)
            db.flush()
            logger.info(f"Admin '{ADMIN_USERNAME}' created.")

            test_users = [
                {"username": "alice", "password": "Alice123!", "role": "user", "email": "alice@example.com"},
                {"username": "bob", "password": "Bob1234!", "role": "user", "email": "bob@example.com"},
                {"username": "tina", "password": "Tina123!", "role": "user", "email": "tina@example.com"},
                {"username": "tea", "password": "Tea1234!", "role": "user", "email": "tea@example.com"},
            ]
            created_users = [admin]
            for u in test_users:
                hashed = auth.get_password_hash(u["password"])
                user = models.User(
                    username=u["username"],
                    password_hash=hashed,
                    role=u["role"],
                    email=u["email"],
                    is_2fa_verified=True  # верификувани за тестирање
                )
                db.add(user)
                created_users.append(user)
            db.commit()
            logger.info(f"Test users created: {[u.username for u in created_users[1:]]}")

            users = [u for u in created_users if u.role == "user"]
            if users:
                test_files = [
                    ("alice_notes.txt", b"Alice's secret note: Buy milk."),
                    ("bob_report.txt", b"Bob's report: Q1 sales are good."),
                    ("shared_meeting.txt", b"Meeting minutes: Project discussion."),
                    ("contract.pdf", b"Dummy PDF content for testing."),
                ]
                docs_created = 0
                for i, (filename, content) in enumerate(test_files):
                    file_hash = crypto.compute_file_hash(content)
                    now = datetime.datetime.utcnow()
                    signature = crypto.sign_hash(file_hash, now)
                    user = users[i % len(users)]

                    record = models.TimestampRecord(
                        filename=filename,
                        file_hash=file_hash,
                        signature=signature,
                        timestamp=now,
                        user_id=user.id
                    )
                    db.add(record)
                    docs_created += 1
                db.commit()
                logger.info(f"Seeded {docs_created} test documents.")
            else:
                logger.warning("No regular users found; skipping document seed.")
        else:
            logger.info("Database already contains users. No seeding performed.")
    except Exception as e:
        logger.error(f"Error during database seeding: {e}")
        db.rollback()
    finally:
        db.close()

    yield

    logger.info("Shutting down application...")


limiter._default_limits = [RATE_LIMIT_GENERAL]

app = FastAPI(
    title="Timestamping Server",
    version="1.0.0",
    lifespan=lifespan,
    description="A secure timestamping server with user authentication and document archiving."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://localhost:5173",
        "https://timestamping.local:5173",
        "http://127.0.0.1:5173",
        "https://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(timestamp.router)
app.include_router(auth_router.router)


@app.get("/")
def root():
    return {
        "message": "Timestamping Server is running",
        "docs": "/docs",
        "health": "OK"
    }