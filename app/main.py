from fastapi import FastAPI
from app.core.config import settings
from app.api.v1 import auth

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    version="1.0.0"
)

# routers
app.include_router(auth.router, prefix="/api/v1")

@app.get("/health")
async def health():
    return {"status": "ok", "app": settings.APP_NAME}