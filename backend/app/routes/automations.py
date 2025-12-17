from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional
from app.dependencies.auth import get_current_user

# BOOT TRACE
print("[BOOT] Loading Automations Router Module...", flush=True)

# Direct Import - Phase 40 verified safe
from app.services.automation_service import run_automation_logic

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
    print(f"[Route] Triggering Automation: {payload.action}")
    res = run_automation_logic(payload.team_id, payload.action, payload.params)
    return res

@router.get("/history")
def get_history(limit: int = 20, current_user: dict = Depends(get_current_user)):
    # Stubbed history for now
    return {"history": []}
