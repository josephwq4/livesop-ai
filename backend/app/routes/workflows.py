from fastapi import APIRouter, HTTPException, Depends
from app.services.workflow_inference import infer_workflow, generate_sop_document, query_similar_events
from app.models.workflow import WorkflowGraph
from typing import Optional
from app.dependencies.auth import get_current_user

router = APIRouter(tags=["workflows"])


@router.get("/{team_id}/workflows")


def get_workflows(team_id: str, current_user: dict = Depends(get_current_user), workflow_id: Optional[str] = None):
    """Get active inferred workflow or specific version for the authenticated user's team"""
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
        
        # If no persistent workflow, return empty structure (Frontend handles "No Workflows Yet")
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

@router.get("/{team_id}/history")
def get_history(team_id: str, current_user: dict = Depends(get_current_user)):
    """Get workflow version history"""
    try:
        from app.repositories.persistence import PersistenceRepository
        repo = PersistenceRepository()
        
        user_id = current_user.get("sub")
        real_team_id = repo.get_or_create_team(f"Team {user_id[:4]}", user_id)
        
        history = repo.get_workflow_history(real_team_id)
        return {
            "success": True, 
            "history": history
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching history: {str(e)}")


@router.get("/{team_id}/search")
def search_knowledge(
    team_id: str, 
    q: str, 
    current_user: dict = Depends(get_current_user)
):
    """Semantic Search (RAG) over team signals"""
    try:
        from app.repositories.persistence import PersistenceRepository
        from app.services.workflow_inference import generate_embeddings
        
        repo = PersistenceRepository()
        
        # Resolve Team
        user_id = current_user.get("sub")
        real_team_id = repo.get_or_create_team(f"Team {user_id[:4]}", user_id)
        
        # 1. Embed Query
        vectors = generate_embeddings([q])
        if not vectors:
             return {"success": False, "results": []}
             
        # 2. Search DB
        results = repo.search_signals(real_team_id, vectors[0])
        return {"success": True, "results": results}
        
    except Exception as e:
        print(f"Search Error: {e}")
        raise HTTPException(status_code=500, detail="Search failed")


@router.post("/{team_id}/infer")
def run_inference(team_id: str, current_user: dict = Depends(get_current_user)):
    """Run workflow inference for a team"""
    try:
        # Pass user_id (sub) to infer_workflow to enable persistence team resolution
        workflow_graph = infer_workflow(team_id, user_id=current_user.get("sub"))
        return {
            "success": True,
            "team_id": team_id,
            "workflow": workflow_graph,
            "message": "Workflow inference completed successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running inference: {str(e)}")


@router.get("/{team_id}/sop")
def get_sop(team_id: str, workflow_id: Optional[str] = None):
    """Generate living SOP document for a team's workflow"""
    try:
        if not workflow_id:
            workflow_id = f"wf_{team_id}_latest"
        
        sop_document = generate_sop_document(team_id, workflow_id)
        return {
            "success": True,
            "team_id": team_id,
            "workflow_id": workflow_id,
            "sop": sop_document,
            "format": "markdown"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating SOP: {str(e)}")


@router.patch("/{team_id}/nodes/{node_id}")
def update_node(
    team_id: str, 
    node_id: str, 
    payload: Dict[str, Any], 
    current_user: dict = Depends(get_current_user)
):
    """Update node metadata (e.g. auto_pilot flag)"""
    try:
        from app.repositories.persistence import PersistenceRepository
        repo = PersistenceRepository()
        
        # In a real app, verify user owns this node's workflow.
        # For now, we trust the update if authenticated.
        
        success = repo.update_node_metadata(node_id, payload)
        if not success:
             raise HTTPException(status_code=404, detail="Node not found")
             
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/test")
def test_workflows():
    """Test endpoint to verify workflows API is working"""
    return {
        "status": "ok",
        "message": "Workflows API is running"
    }
