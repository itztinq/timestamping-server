import uvicorn
from app.config import PRIVATE_KEY_PATH, CERTIFICATE_PATH, PORT

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=PORT,
        ssl_keyfile=str(PRIVATE_KEY_PATH),
        ssl_certfile=str(CERTIFICATE_PATH),
        reload=True,
        reload_excludes=["venv/*", "**/venv/**/*"]
    )