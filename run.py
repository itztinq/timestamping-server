import uvicorn
from app.config import PORT
import ssl

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=PORT,
        ssl_keyfile="pki/server/server.key.pem",
        ssl_certfile="pki/server/server.fullchain.pem",
        ssl_ca_certs="pki/intermediate-ca/certs/ca-chain.cert.pem",
        ssl_cert_reqs=ssl.CERT_REQUIRED,
        ssl_ciphers="ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS",
        reload=True,
        reload_excludes=["venv/*", "**/venv/**/*"]
    )