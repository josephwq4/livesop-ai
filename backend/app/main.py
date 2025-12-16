from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from pathlib import Path

# Build path to backend/.env
# app/main.py -> backend/app/main.py. Parent is backend/app. Parent.parent is backend.
env_path = Path(__file__).resolve().parent.parent / ".env"
print(f"Loading env from: {env_path}")
load_dotenv(dotenv_path=env_path)

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

# from app.routes import integrations, workflows, automations, webhooks, usage, settings, health, knowledge
# Temporarily minimal imports for debugging
from app.routes import health
from app.dependencies.auth import get_current_user

from app.middleware.logging import AuditLoggingMiddleware

# Initialize Rate Limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="LiveSOP AI",
    description="AI-powered workflow inference and automation platform",
    version="1.0.0"
)

# Register Limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Register Audit Logging
app.add_middleware(AuditLoggingMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173", 
        "https://livesopai.vercel.app",  # Your Production URL
        "https://livesop-ai.vercel.app"  # Alternative (just in case)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with Authentication Lock
print("[INFO] Loading routers with Auth Enabled")
# app.include_router(
#     integrations.router, 
#     prefix="/integrations", 
#     dependencies=[Depends(get_current_user)]
# )

# app.include_router(
#     workflows.router, 
#     prefix="/workflows", 
#     dependencies=[Depends(get_current_user)]
# )
# app.include_router(
#     automations.router, 
#     prefix="/automations", 
#     dependencies=[Depends(get_current_user)]
# )

# app.include_router(
#     usage.router, 
#     prefix="/usage", 
#     dependencies=[Depends(get_current_user)]
# )

# app.include_router(
#     settings.router, 
#     dependencies=[Depends(get_current_user)]
# )

# app.include_router(
#     knowledge.router,
#     prefix="/knowledge", 
#     dependencies=[Depends(get_current_user)]
# )

# Webhooks (Public endpoint with Internal Signature Verification)
# app.include_router(
#     webhooks.router,
#     prefix="/webhooks"
# )

# Health checks (Public endpoint for monitoring)
app.include_router(
    health.router,
    prefix=""  # No prefix - accessible at /health
)


@app.get("/")
@limiter.limit("50/minute")
def root(request: Request):
    """Root endpoint (Public)"""
    return {
        "message": "LiveSOP AI (Maintenance Mode)",
        "version": "1.0.0",
        "status": "running",
        "auth": "enabled"
    }


@app.get("/health")
@limiter.limit("100/minute")
def health_check(request: Request):
    """Health check endpoint (Public)"""
    return {
        "status": "healthy",
        "service": "LiveSOP AI Backend"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
