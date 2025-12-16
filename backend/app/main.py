from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from pathlib import Path

env_path = Path(__file__).resolve().parent.parent / ".env"
print(f"Loading env from: {env_path}")
load_dotenv(dotenv_path=env_path)

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

# IMPORTANT: Enable ALL Routers (Final Check)
from app.routes import health, usage, settings, integrations, automations, workflows, knowledge, webhooks

from app.dependencies.auth import get_current_user
from app.middleware.logging import AuditLoggingMiddleware

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

print("[INFO] Loading routers...")

# Core Integrations (CONFIRMED SAFE)
app.include_router(integrations.router, prefix="/integrations", dependencies=[Depends(get_current_user)])

# ML Workflows (Stubbed ML, Router Safe)
app.include_router(workflows.router, prefix="/workflows", dependencies=[Depends(get_current_user)])

# Knowledge Base (Testing this!)
app.include_router(knowledge.router, prefix="/knowledge", dependencies=[Depends(get_current_user)])

# Basic CRUD
app.include_router(usage.router, prefix="/usage", dependencies=[Depends(get_current_user)])
app.include_router(settings.router, dependencies=[Depends(get_current_user)])

# Automations (CONFIRMED SAFE)
app.include_router(automations.router, prefix="/automations", dependencies=[Depends(get_current_user)])

# Webhooks (Testing This! Uses trigger_engine)
app.include_router(webhooks.router, prefix="/webhooks")

# Health
app.include_router(health.router, prefix="")

@app.get("/")
@limiter.limit("50/minute")
def root(request: Request):
    return {"message": "LiveSOP AI (Maintenance Mode)", "status": "running"}

@app.get("/health")
def health_check(request: Request):
    return {"status": "healthy", "service": "LiveSOP AI Backend"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
