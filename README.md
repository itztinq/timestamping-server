# Timestamping Server

A secure backend service for timestamping and archiving documents. Users can upload files, receive a cryptographically signed proof of existence, and later verify document integrity. Built with FastAPI, JWT authentication, and RSA digital signatures.

## Features

- **User Authentication**: Register and login with JWT tokens. Passwords are hashed using bcrypt.
- **Role-based Access**: Regular users see only their own documents and admins can view all.
- **Document Timestamping**: Upload a document, compute its SHA-256 hash, and sign it with the server's private key together with the current timestamp.
- **Verification**: Anyone can verify a document by uploading it, the server checks if the hash exists and the signature is valid.
- **Certificate Download**: The server's public certificate can be downloaded for client-side signature verification.
- **Auto-seeding**: On first run, the database is automatically populated with an admin user, test users, and sample documents.
- **HTTPS**: Secure communication with self-signed certificates (for development).

## Tech Stack

- **Backend**: FastAPI
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: JWT (python-jose) + bcrypt (passlib)
- **Cryptography**: RSA signatures (cryptography library)
- **SSL**: OpenSSL self-signed certificates
- **Configuration**: python-dotenv

## Prerequisites

- Python 3.9 or higher
- Git
- OpenSSL (to generate certificates)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/itztinq/timestamping-server.git
   cd timestamping-server
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Generate self-signed SSL certificates (for development):
   ```bash
   mkdir certs
   openssl req -x509 -newkey rsa:2048 -keyout certs/server.key -out certs/server.crt -days 365 -nodes
   ```
5. Copy the environment example file and edit it:
   ```bash
   cp .env.example .env
   ```
   > Generate a secure AUTH_SECRET (e.g., openssl rand -base64 32) and set it in .env.
6. Start
   ```bash
   python run.py
   ```
   The server will be available at https://localhost:8443

## Database Seeding
On the very first run, the database is automatically seeded with:
| Role    | Username | Password    |
|---------|----------|-------------|
| Admin   | `admin`  | `Admin123!` |
| User    | `alice`  | `Alice123!` |
| User    | `bob`    | `Bob1234!`  |
| User    | `tina`   | `Tina123!`  |
| User    | `tea`    | `Tea1234!`  |
> Note: The admin password can be changed in the .env file before starting the server. Test user passwords are hardcoded but can be modified in the seeding logic.

## Project Structure
```agsl
timestamping-server/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app & lifespan
│   ├── database.py           # SQLAlchemy setup
│   ├── models.py             # DB models (User, TimestampRecord)
│   ├── schemas.py            # Pydantic schemas
│   ├── crypto.py             # Hashing, signing, verification
│   ├── auth.py               # JWT & password handling
│   ├── config.py             # Environment variables
│   └── routers/
│       ├── auth.py           # /auth endpoints
│       └── timestamp.py      # /api/timestamps endpoints
├── certs/                     # SSL certificates
├── .env.example               # Template for environment variables
├── .gitignore
├── requirements.txt
├── run.py                     # Entry point for uvicorn
└── README.md
```
