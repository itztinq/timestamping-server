import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent.parent
CERTS_DIR = BASE_DIR / "certs"
DB_FILE = BASE_DIR / "timestamps.db"

PRIVATE_KEY_PATH = CERTS_DIR / "server.key"
CERTIFICATE_PATH = CERTS_DIR / "server.crt"

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "Admin123!")

AUTH_SECRET = os.getenv("AUTH_SECRET", "change-this-in-production")

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_FILE}")
PORT = int(os.getenv("PORT", 8443))

RATE_LIMIT_AUTH = os.getenv("RATE_LIMIT_AUTH", "5/minute")
RATE_LIMIT_UPLOAD = os.getenv("RATE_LIMIT_UPLOAD", "10/hour")
RATE_LIMIT_DELETE = os.getenv("RATE_LIMIT_DELETE", "10/hour")
RATE_LIMIT_GENERAL = os.getenv("RATE_LIMIT_GENERAL", "30/minute")