# Timestamping Server

A secure, full-stack application for timestamping and archiving documents. Users can upload files, receive a cryptographically signed proof of existence, and later verify document integrity. Built with FastAPI (Backend), React + Vite (Frontend), and features a complete Public Key Infrastructure (PKI) for mTLS (Mutual TLS) communication.

## Features

- **User Authentication**: Register and login with JWT tokens. Passwords are hashed using bcrypt.
- **Two-Factor Authentication (2FA)**: **Mandatory for all users**. After login, a one-time code is sent to the user's email. The code must be entered to complete the login process.
- **Role-based Access**: Regular users see only their own documents and admins can view all.
- **Document Timestamping**: Upload a document, compute its SHA-256 hash, and securely sign it with the server's RSA private key combined with the current UTC timestamp.
- **Verification**: Anyone can verify a document by uploading it, the server checks if the hash exists and the signature is valid.
- **Certificate Download**: The server's public certificate can be downloaded for client-side signature verification.
- **Auto-seeding**: On first run, the database is automatically populated with an admin user, test users, and sample documents.
- **Full PKI & mTLS**: Automated generation of Root CA, Intermediate CA, Server, and Client certificates for highly secure, two-way HTTPS communication.

## Tech Stack

- **Backend**: FastAPI
- **Frontend**: React.js with Vite
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: JWT (python-jose) + bcrypt (passlib)
- **2FA**: Email OTP via SMTP 
- **Cryptography**: RSA signatures (cryptography library)
- **Security**: mTLS with OpenSSL-compatible certificates
- **Configuration**: python-dotenv

## Prerequisites

- Python 3.9+
- Node.js & npm
- Git
- OpenSSL

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/itztinq/timestamping-server.git
   cd timestamping-server
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/Scripts/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Generate PKI & Certificates:
   This project uses a full PKI structure for mTLS. Run the automated script to generate the Root CA, Intermediate CA, and the Server/Client certificates.
   ```bash
   python generate_pki.py
   ```
   > Note: This will populate the pki/ directory. Private keys are automatically ignored by Git for security.
6. Copy the environment example file and edit it:
   ```bash
   cp .env.example .env
   ```
   > Generate a secure AUTH_SECRET (e.g., openssl rand -base64 32) and set it in .env. Important: For 2FA to work, you must configure email settings (see Email Configuration below).
7. Install Client Certificate (Browser mTLS)
   Before starting the client, you must install the generated client certificate in your OS/Browser to authenticate with the server:
   - Navigate to `pki/client/`
   - Double-click on `client.p12`
   - Enter the password: `changeit`
   - Complete the import wizard and restart your browser.
8. Running the Application
   You will need two separate terminal windows to run both the Backend and Frontend.
   Terminal 1 (Backend):
   ```bash
   python run.py
   ```
   > The FastAPI backend will start at https://localhost:8443
   Terminal 2 (Frontend):
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   > The React frontend will start at https://localhost:5173.

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
│   ├── main.py              # FastAPI app & lifespan setup
│   ├── database.py          # SQLAlchemy setup
│   ├── models.py            # DB models (User, TimestampRecord)
│   ├── schemas.py           # Pydantic validation schemas
│   ├── crypto.py            # Hashing, signing, and verification logic
│   ├── auth.py              # JWT & password handling
│   ├── config.py            # Environment variables loader
│   └── routers/             # API Endpoints
├── frontend/                # React + Vite application
│   ├── public/              
│   │   └── vite.svg         # Static assets
│   ├── src/
│   ├── api/             # Axios configs and API client calls
│   │   ├── assets/          # Images and styling assets
│   │   ├── components/      # Reusable React components
│   │   ├── utils/           # Helper functions
│   │   ├── App.css          # App-specific styles
│   │   ├── App.jsx          # Main application component
│   │   ├── index.css        # Global CSS styles
│   │   └── main.jsx         # React DOM rendering entry point
│   ├── eslint.config.js     # Linter configuration
│   ├── index.html           # Main HTML template
│   ├── package-lock.json    # Dependency lockfile
│   ├── package.json         # Node.js dependencies and scripts
│   └── vite.config.js       # Vite configuration (HTTPS bound to PKI)
├── pki/                     # Secure Public Key Infrastructure
│   ├── root-ca/             # Root Certificate Authority
│   ├── intermediate-ca/     # Intermediate Certificate Authority
│   ├── server/              # Server certificates (FastAPI)
│   └── client/              # Client certificates (mTLS / Browser)
├── generate_pki.py          # Script to auto-generate the PKI chain
├── .env.example             # Template for environment variables
├── .gitattributes           
├── .gitignore               
├── requirements.txt         # Python dependencies
├── run.py                   # Entry point for Uvicorn
└── README.md                

```
