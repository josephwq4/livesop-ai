from fastapi import APIRouter, HTTPException, Depends, Response
from app.models.workflow import WorkflowGraph
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from app.dependencies.auth import get_current_user
from app.repositories.persistence import PersistenceRepository
from app.services.workflow_inference import infer_workflow, generate_sop_document, query_similar_events

# BOOT TRACE
print("[BOOT] Loading Workflows Router...", flush=True)

router = APIRouter(tags=["workflows"])

class WorkflowNodeBatchUpdate(BaseModel):
    id: str
    label: Optional[str] = None
    description: Optional[str] = None
    auto_run_enabled: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None

@router.get("/{team_id}/workflows")
def get_workflows(
    team_id: str, 
    response: Response,
    current_user: dict = Depends(get_current_user), 
    workflow_id: Optional[str] = None
):
    """
    Get active inferred workflow or specific version for the authenticated user's team.
    """
    try:
        repo = PersistenceRepository()
        
        # Resolve Team from User (Single Tenant MVP)
        user_id = current_user.get("sub")
        real_team_id = repo.get_or_create_team(f"Team {user_id[:4]}", user_id)
        
        if workflow_id:
            workflow_graph = repo.get_workflow_by_id(workflow_id, real_team_id)
        else:
            workflow_graph = repo.get_active_workflow(real_team_id)
        
        response.headers["Cache-Control"] = "private, max-age=30"
        
        if not workflow_graph:
            return {
                "success": True,
                "team_id": real_team_id,
                "workflow": None,
                "message": "No workflow found"
            }
            
        return {
            "success": True,
            "team_id": real_team_id,
            "workflow": workflow_graph
        }
    except Exception as e:
        print(f"Workflow Fetch Error: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching workflows: {str(e)}")

@router.post("/{team_id}/infer")
def run_inference(team_id: str, current_user: dict = Depends(get_current_user)):
    """Trigger AI inference to generate workflow from events"""
    try:
        user_id = current_user.get("sub")
        workflow = infer_workflow(team_id, user_id)
        return {"success": True, "workflow": workflow}
    except Exception as e:
        print(f"Inference Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{team_id}/history")
def get_history(team_id: str, limit: int = 10, current_user: dict = Depends(get_current_user)):
    try:
        repo = PersistenceRepository()
        user_id = current_user.get("sub")
        real_team_id = repo.get_or_create_team(f"Team {user_id[:4]}", user_id)
        
        history = repo.get_workflow_history(real_team_id, limit)
        return {"history": history}
    except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))

@router.get("/{team_id}/sop")
def get_sop(team_id: str, workflow_id: Optional[str] = None, current_user: dict = Depends(get_current_user)):
    try:
        sop_content = generate_sop_document(team_id, workflow_id)
        return {"sop": sop_content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{team_id}/search")
def search_knowledge(team_id: str, q: str, current_user: dict = Depends(get_current_user)):
    try:
        results = query_similar_events(team_id, q)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
