from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from pathlib import Path

# 1. Load Env
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

# 2. Dependencies
from app.dependencies.auth import get_current_user
from app.middleware.logging import AuditLoggingMiddleware

# 3. Routers (Phase 36: Usage + Settings)
from app.routes import health, usage, settings

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="LiveSOP AI", version="1.0.0")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(AuditLoggingMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173", 
        "https://livesopai.vercel.app",
        "https://livesop-ai.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Active Routers
app.include_router(usage.router, prefix="/usage", dependencies=[Depends(get_current_user)])
app.include_router(settings.router, dependencies=[Depends(get_current_user)])
app.include_router(health.router, prefix="")

@app.get("/")
@limiter.limit("50/minute")
def root(request: Request):
    return {"message": "LiveSOP AI (Stable Base Active)", "status": "running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
