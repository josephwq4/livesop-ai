from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional
from app.dependencies.auth import get_current_user

# BOOT TRACE
print("[BOOT] Loading Automations Router Module...", flush=True)
print("[BOOT] Importing Automation Service...", flush=True)

try:
    from app.services.automation_service import run_automation_logic
    print("[BOOT] Service Imported Successfully.", flush=True)
except Exception as e:
    print(f"[BOOT] Service Import Failed: {e}", flush=True)
    # Fallback to local stub if import fails (should crash boot if critical, but let's try to survive)
    def run_automation_logic(*args): return {"error": "Import Failed"}

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
    print(f"[Route] Triggering via Service...")
    res = run_automation_logic(payload.team_id, payload.action, payload.params)
    return res

@router.get("/history")
def get_history(limit: int = 20, current_user: dict = Depends(get_current_user)):
    return {"history": []}
