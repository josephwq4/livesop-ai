from fastapi import APIRouter, HTTPException, Depends, Response
from app.models.workflow import WorkflowGraph
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from app.dependencies.auth import get_current_user

# Stub logic to identify import crash
def infer_workflow(*args, **kwargs): return {}
def generate_sop_document(*args, **kwargs): return "SOP stub"
def query_similar_events(*args, **kwargs): return []

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
        from app.repositories.persistence import PersistenceRepository
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
        raise HTTPException(status_code=500, detail=f"Error fetching workflows: {str(e)}")

@router.get("/test_models")
def test_models():
    # Instantiate to test runtime
    node = WorkflowNodeBatchUpdate(id="1")
    return {"status": "ok", "node": node.dict()}

# PHASE 24 RESTRICTION: Comment out all other endpoints to isolate toxicity
# @router.get("/{team_id}/history")
# def get_history...

# @router.get("/{team_id}/search")
# def search_knowledge...

# @router.post("/{team_id}/infer")
# def run_inference...

# @router.get("/{team_id}/sop")
# def get_sop...

# @router.put("/{team_id}/{workflow_id}/nodes")
# def update_workflow_nodes...

# @router.patch("/{team_id}/nodes/{node_id}")
# def update_node...
