from fastapi import APIRouter
from app.repositories.persistence import PersistenceRepository

router = APIRouter(tags=["health"])

@router.get("/health")
def health_check():
    return {"status": "ok", "version": "1.0.0-phase46"} 

@router.get("/health_db")
def health_db():
    """Diagnostic endpoint to check DB connectivity"""
    try:
        repo = PersistenceRepository()
        res = repo.db.table("teams").select("count", count="exact").limit(1).execute()
        return {"status": "ok", "db": "connected", "teams_count": res.count}
    except Exception as e:
        return {"status": "error", "message": str(e)}
