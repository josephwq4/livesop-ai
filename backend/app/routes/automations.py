from fastapi import APIRouter, HTTPException, Depends
from app.services.automation_service import run_automation_logic
from pydantic import BaseModel
from typing import Dict, Any, Optional
from app.dependencies.auth import get_current_user

router = APIRouter(tags=["automations"])

class TriggerRequest(BaseModel):
    team_id: str
    action: str
    params: Dict[str, Any]

@router.post("/trigger")
def trigger_automation(
    payload: TriggerRequest,
    current_user: dict = Depends(get_current_user)
):
    try:
        res = run_automation_logic(payload.team_id, payload.action, payload.params)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
