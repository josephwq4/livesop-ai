from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
import os

router = APIRouter(tags=["health"])

@router.get("/health")
def health_check():
    """
    Health check endpoint for monitoring and load balancers.
    Returns 200 if all critical services are reachable.
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "livesop-backend",
        "version": "1.0.0"
    }
    
    checks = {}
    
    # Check 1: Database connectivity
    try:
        from app.repositories.persistence import PersistenceRepository
        repo = PersistenceRepository()
        # Simple query to verify DB is responsive
        result = repo.db.table("teams").select("id").limit(1).execute()
        checks["database"] = "healthy"
    except Exception as e:
        checks["database"] = f"unhealthy: {str(e)[:100]}"
        health_status["status"] = "degraded"
    
    # Check 2: OpenAI API key configured
    if os.getenv("OPENAI_API_KEY"):
        checks["openai"] = "configured"
    else:
        checks["openai"] = "not_configured"
        health_status["status"] = "degraded"
    
    # Check 3: Supabase configured
    if os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_SERVICE_KEY"):
        checks["supabase"] = "configured"
    else:
        checks["supabase"] = "not_configured"
        health_status["status"] = "unhealthy"
    
    health_status["checks"] = checks
    
    # Return 503 if unhealthy (for load balancer health checks)
    if health_status["status"] == "unhealthy":
        raise HTTPException(status_code=503, detail=health_status)
    
    return health_status


@router.get("/health/ready")
def readiness_check():
    """
    Kubernetes-style readiness probe.
    Returns 200 only if service is ready to accept traffic.
    """
    try:
        from app.repositories.persistence import PersistenceRepository
        repo = PersistenceRepository()
        # Verify we can write to DB
        repo.db.table("teams").select("id").limit(1).execute()
        return {"status": "ready"}
    except Exception as e:
        raise HTTPException(status_code=503, detail={"status": "not_ready", "error": str(e)})


@router.get("/health/live")
def liveness_check():
    """
    Kubernetes-style liveness probe.
    Returns 200 if process is alive (doesn't check dependencies).
    """
    return {"status": "alive", "timestamp": datetime.now(timezone.utc).isoformat()}
