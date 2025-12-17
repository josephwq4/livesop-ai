from fastapi import APIRouter, HTTPException, Depends
from app.dependencies.auth import get_current_user
from app.repositories.persistence import PersistenceRepository

router = APIRouter(tags=["usage"])

@router.get("/")
def get_team_usage(current_user: dict = Depends(get_current_user)):
    """Get current team usage and limits"""
    try:
        repo = PersistenceRepository()
        user_id = current_user.get("sub")
        team_id = repo.get_or_create_team(f"Team {user_id[:4]}", user_id)
        
        # Query Usage
        res = repo.db.table("team_usage").select("*").eq("team_id", team_id).maybe_single().execute()
        
        usage_data = res.data
        
        if not usage_data:
            # Create default if not exists
            new_usage = {
                "team_id": team_id, 
                "automation_limit": 100, 
                "automation_count": 0,
                "plan_tier": "free"
            }
            try:
                repo.db.table("team_usage").insert(new_usage).execute()
                usage_data = new_usage
            except Exception as e:
                print(f"[DB Error] Failed to create usage record: {e}")
                # Fallback: Return the default object anyway so frontend works
                # (Likely cause: Race condition or permissions)
                usage_data = new_usage

        return {
            "success": True,
            "usage": usage_data
        }
            
    except Exception as e:
        print(f"Usage Endpoint Critical Error: {e}")
        # Even on critical error, return a fallback to avoid crashing dashboard
        return {
            "success": False,
            "usage": {
                "automation_limit": 0,
                "automation_count": 0,
                "plan_tier": "error"
            },
            "error": str(e)
        }
