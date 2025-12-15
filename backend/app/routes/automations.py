from fastapi import APIRouter, HTTPException, Depends, Body
from typing import Dict, Any
from app.dependencies.auth import get_current_user
from app.services.integration_clients import send_slack_message, create_jira_issue
import os

router = APIRouter(tags=["automations"])

@router.post("/{team_id}/execute")
def execute_automation(
    team_id: str, 
    payload: Dict[str, Any] = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Execute an automated action (Slack, Jira, etc.)
    Payload: { "action": "type", "params": {...} }
    """
    action_type = payload.get("action")
    params = payload.get("params", {})
    
    if not action_type:
        raise HTTPException(status_code=400, detail="Missing 'action' in payload")

    print(f"[Automation] Executing {action_type} for team {team_id} by user {current_user.get('sub')}")

    result = {"success": False, "message": "Unknown action"}

    try:
        if action_type == "create_jira_ticket":
            # Defaults
            project = params.get("project") or os.getenv("JIRA_PROJECT", "PROJ")
            summary = params.get("summary", "New Task from LiveSOP")
            desc = params.get("description", "Created via LiveSOP Automation")
            
            # Execute
            res = create_jira_issue("env", project, summary, desc)
            if res["success"]:
                result = {
                    "success": True, 
                    "message": f"Created Jira Ticket {res['key']}",
                    "url": res["url"]
                }
            else:
                raise Exception(res.get("error", "Unknown Jira Error"))

        elif action_type == "slack_notify":
            channel = params.get("channel") or os.getenv("SLACK_CHANNELS", "general").split(",")[0]
            text = params.get("message", "Hello from LiveSOP")
            token = os.getenv("SLACK_TOKEN", "")
            
            res = send_slack_message(token, channel, text)
            if res["success"]:
                result = {"success": True, "message": "Slack message sent"}
            else:
                raise Exception(res.get("error", "Unknown Slack Error"))

        else:
             raise HTTPException(status_code=400, detail=f"Unsupported action: {action_type}")

        return result

    except Exception as e:
        print(f"[Automation Error] {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{team_id}/live_feed")
def get_live_feed(
    team_id: str, 
    limit: int = 10,
    current_user: dict = Depends(get_current_user)
):
    """Get recent escalations/automations for the live dashboard"""
    try:
        from app.repositories.persistence import PersistenceRepository
        repo = PersistenceRepository()
        
        # Helper to resolve team if needed, but path param is used. 
        # Ideally verify user access to team_id here.
        user_id = current_user.get("sub")
        # For simplicity in MVP, we might trust the ID or verify ownership:
        # real_team_id = repo.get_or_create_team(...) matches team_id check
        
        # Fetch runs with signals
        # select("*, inference_run_signals(raw_signals(*))")
        try:
            res = repo.db.table("inference_runs")\
                .select("*, inference_run_signals(signal_id, raw_signals(*))")\
                .eq("team_id", team_id)\
                .order("started_at", desc=True)\
                .limit(limit)\
                .execute()
        except Exception as e:
            # Fallback if join syntax fails or table empty
            print(f"Join query failed: {e}")
            return {"feed": []}
            
        feed = []
        for r in res.data:
            # Flatten structure
            signals_join = r.get("inference_run_signals", [])
            primary_signal = {}
            if signals_join:
                 # It returns a list of objects { signal_id: ..., raw_signals: {...} }
                 primary_signal = signals_join[0].get("raw_signals") or {}

            feed.append({
                "id": r["id"],
                "time": r["started_at"],
                "channel": primary_signal.get("metadata", {}).get("channel", "Unknown"),
                "customer": primary_signal.get("actor", "Unknown"),
                "confidence": r.get("model_config", {}).get("confidence", 0.0), # Default 0
                "action": r["trigger_type"],
                "status": r["status"]
            })
            
        return {"feed": feed}

    except Exception as e:
        print(f"Live Feed Error: {e}")
        # Return empty feed instead of crash
        return {"feed": []}
