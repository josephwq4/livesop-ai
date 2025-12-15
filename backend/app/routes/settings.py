from fastapi import APIRouter, HTTPException, Depends, Body
from typing import Dict, Any
from app.dependencies.auth import get_current_user
from app.repositories.persistence import PersistenceRepository

router = APIRouter(tags=["settings"])

@router.post("/auto_pilot/global")
def toggle_global_auto_pilot(
    payload: Dict[str, Any] = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Toggle global Auto-Pilot kill switch for the authenticated user's team.
    Payload: { "enabled": true/false }
    """
    try:
        repo = PersistenceRepository()
        user_id = current_user.get("sub")
        
        # Resolve team
        team_id = repo.get_or_create_team(f"Team {user_id[:4]}", user_id)
        
        enabled = payload.get("enabled")
        if enabled is None:
            raise HTTPException(status_code=400, detail="Missing 'enabled' field in payload")
        
        success = repo.set_team_auto_pilot_status(team_id, enabled)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update Auto-Pilot status")
        
        status_text = "enabled" if enabled else "disabled"
        print(f"[Settings] Global Auto-Pilot {status_text} for team {team_id}")
        
        return {
            "success": True,
            "team_id": team_id,
            "auto_pilot_enabled": enabled,
            "message": f"Global Auto-Pilot {status_text}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/auto_pilot/node/{node_id}")
def toggle_node_auto_run(
    node_id: str,
    payload: Dict[str, Any] = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Toggle Auto-Run for a specific workflow node.
    Payload: { "enabled": true/false }
    """
    try:
        repo = PersistenceRepository()
        
        enabled = payload.get("enabled")
        if enabled is None:
            raise HTTPException(status_code=400, detail="Missing 'enabled' field in payload")
        
        # Verify user owns this node's workflow (simplified for MVP - trust auth)
        success = repo.set_node_auto_run_status(node_id, enabled)
        
        if not success:
            raise HTTPException(status_code=404, detail="Node not found or update failed")
        
        status_text = "enabled" if enabled else "disabled"
        print(f"[Settings] Auto-Run {status_text} for node {node_id}")
        
        return {
            "success": True,
            "node_id": node_id,
            "auto_run_enabled": enabled,
            "message": f"Auto-Run {status_text} for node {node_id}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/auto_pilot/status")
def get_auto_pilot_status(current_user: dict = Depends(get_current_user)):
    """
    Get current Auto-Pilot status for the authenticated user's team.
    Returns global status and list of nodes with their individual flags.
    """
    try:
        repo = PersistenceRepository()
        user_id = current_user.get("sub")
        
        # Resolve team
        team_id = repo.get_or_create_team(f"Team {user_id[:4]}", user_id)
        
        # Get global status
        global_enabled = repo.get_team_auto_pilot_status(team_id)
        
        # Get active workflow and node statuses
        workflow = repo.get_active_workflow(team_id)
        node_statuses = []
        
        if workflow and workflow.get("nodes"):
            for node in workflow["nodes"]:
                node_id = node.get("id")
                node_enabled = repo.get_node_auto_run_status(node_id)
                node_statuses.append({
                    "node_id": node_id,
                    "label": node.get("data", {}).get("label"),
                    "auto_run_enabled": node_enabled
                })
        
        return {
            "success": True,
            "team_id": team_id,
            "global_auto_pilot_enabled": global_enabled,
            "nodes": node_statuses
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
