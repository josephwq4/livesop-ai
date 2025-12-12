from fastapi import APIRouter, HTTPException
from app.services.automation_runner import automation_runner
from app.models.workflow import AutomationRequest
from typing import Optional, Dict, Any

router = APIRouter(tags=["automations"])


@router.post("/{team_id}/run/{workflow_id}")
def execute_automation(team_id: str, workflow_id: str, parameters: Optional[Dict[str, Any]] = None):
    """Execute a workflow automation"""
    try:
        result = automation_runner.run_automation(team_id, workflow_id, parameters)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing automation: {str(e)}")


@router.get("/{team_id}/history")
def get_automation_history(team_id: str, limit: int = 50):
    """Get automation execution history for a team"""
    try:
        history = automation_runner.get_automation_history(team_id, limit)
        return {
            "success": True,
            "team_id": team_id,
            "count": len(history),
            "history": history
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching history: {str(e)}")


@router.post("/{team_id}/schedule/{workflow_id}")
def schedule_automation(team_id: str, workflow_id: str, schedule: str, parameters: Optional[Dict[str, Any]] = None):
    """Schedule a recurring automation"""
    try:
        result = automation_runner.schedule_automation(team_id, workflow_id, schedule, parameters)
        return {
            "success": True,
            "scheduled_automation": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scheduling automation: {str(e)}")


@router.get("/test")
def test_automations():
    """Test endpoint to verify automations API is working"""
    return {
        "status": "ok",
        "message": "Automations API is running"
    }
