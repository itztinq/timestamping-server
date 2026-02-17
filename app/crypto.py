import hashlib
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
from .config import PRIVATE_KEY_PATH, CERTIFICATE_PATH
import base64
from datetime import datetime

def load_private_key():
    with open(PRIVATE_KEY_PATH, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend=default_backend()
        )
    return private_key

def load_public_key_from_cert():
    from cryptography import x509
    with open(CERTIFICATE_PATH, "rb") as cert_file:
        cert = x509.load_pem_x509_certificate(cert_file.read(), default_backend())
    return cert.public_key()

def compute_file_hash(file_bytes: bytes) -> str:
    sha256 = hashlib.sha256()
    sha256.update(file_bytes)
    return sha256.hexdigest()

def sign_hash(hash_hex: str, timestamp: datetime) -> str:
    private_key = load_private_key()
    
    data = f"{hash_hex}|{timestamp.isoformat()}".encode()
    signature = private_key.sign(
        data,
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    return base64.b64encode(signature).decode()

def verify_signature(hash_hex: str, timestamp: datetime, signature_b64: str) -> bool:
    public_key = load_public_key_from_cert()
    data = f"{hash_hex}|{timestamp.isoformat()}".encode()
    signature = base64.b64decode(signature_b64)
    try:
        public_key.verify(
            signature,
            data,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        return True
    except Exception:
        return False