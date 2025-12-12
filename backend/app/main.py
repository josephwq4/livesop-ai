from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import integrations, workflows, automations

app = FastAPI(
    title="LiveSOP AI",
    description="AI-powered workflow inference and automation platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(integrations.router, prefix="/integrations")
app.include_router(workflows.router, prefix="/workflows")
app.include_router(automations.router, prefix="/automations")


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Welcome to LiveSOP AI",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "integrations": "/integrations",
            "workflows": "/workflows",
            "automations": "/automations",
            "docs": "/docs"
        }
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "LiveSOP AI Backend"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
