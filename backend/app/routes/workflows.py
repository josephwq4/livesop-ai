from fastapi import APIRouter, HTTPException, Depends
from app.services.workflow_inference import infer_workflow, generate_sop_document, query_similar_events
from app.models.workflow import WorkflowGraph
from typing import Optional
from app.dependencies.auth import get_current_user

router = APIRouter(tags=["workflows"])


@router.get("/{team_id}/workflows")
def get_workflows(team_id: str):
    """Get inferred workflows for a team"""
    try:
        workflow_graph = infer_workflow(team_id)
        return {
            "success": True,
            "team_id": team_id,
            "workflow": workflow_graph
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching workflows: {str(e)}")


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


@router.get("/{team_id}/search")
def search_workflows(team_id: str, query: str, limit: int = 10):
    """Search for similar workflow events using vector similarity"""
    try:
        results = query_similar_events(team_id, query, n_results=limit)
        return {
            "success": True,
            "team_id": team_id,
            "query": query,
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching workflows: {str(e)}")


@router.get("/test")
def test_workflows():
    """Test endpoint to verify workflows API is working"""
    return {
        "status": "ok",
        "message": "Workflows API is running"
    }
