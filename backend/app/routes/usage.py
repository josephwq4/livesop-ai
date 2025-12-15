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
            # Note: RLS might block insert if not owner, but get_or_create_team ensures we are owner of this team or it exists.
            # Assuming backend service role override isn't needed if we are the owner.
            # But wait, PersistenceRepository uses 'get_supabase_client()' which usually uses SERVICE_KEY?
            # Let's check PersistenceRepository init.
            # It uses get_supabase_client(). If that uses service key, we are god mode.
            # If it uses anon key + user token, we are user.
            
            repo.db.table("team_usage").insert(new_usage).execute()
            usage_data = new_usage
            
        return {
            "success": True,
            "usage": usage_data
        }
            
    except Exception as e:
        print(f"Usage Error: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching usage: {str(e)}")
