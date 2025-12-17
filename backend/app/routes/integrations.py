from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, List
from app.dependencies.auth import get_current_user
from app.services.integration_clients import fetch_slack_events, fetch_jira_issues
from app.repositories.persistence import PersistenceRepository

# BOOT TRACE
print("[BOOT] Loading Integrations Router...", flush=True)

router = APIRouter(tags=["integrations"])

@router.get("/slack/events")
def get_slack_events(token: str, channel: str, current_user: dict = Depends(get_current_user)):
    """Fetch recent messages from a channel"""
    events = fetch_slack_events(token, channel)
    return {"events": events}

@router.get("/jira/issues")
def get_jira_issues(api_key: str, project: str, email: str, server: str, current_user: dict = Depends(get_current_user)):
    """Fetch recent Jibra issues"""
    issues = fetch_jira_issues(api_key, project, email, server)
    return {"issues": issues}

@router.get("/status")
def get_integrations_status(current_user: dict = Depends(get_current_user)):
    return {"slack": "active", "jira": "active"}

@router.get("/debug_slack")
def debug_slack(current_user: dict = Depends(get_current_user)):
    """Debug endpoint to verify DB configs and Slack connectivity"""
    repo = PersistenceRepository()
    user_id = current_user.get("sub")
    team_id = repo.get_or_create_team(f"Team {user_id[:4]}", user_id)
    configs = repo.get_team_integrations(team_id)
    
    results = []
    for c in configs:
        conf = c.get("config") or {}
        token = conf.get("token")
        chan = c.get("channel_id")
        
        entry = {"channel_id": chan, "has_token": bool(token), "status": "pending"}
        
        try:
            if not token:
                entry["status"] = "missing_token"
            elif not chan:
                entry["status"] = "missing_channel"
            else:
                msgs = fetch_slack_events(token, chan)
                entry["msg_count"] = len(msgs)
                entry["last_msg"] = msgs[0]['text'] if msgs else None
                entry["status"] = "success" if msgs else "empty_or_failed"
        except Exception as e:
            entry["status"] = f"error: {str(e)}"
            
        results.append(entry)
        
    return {
        "team_id": team_id,
        "config_count": len(configs),
        "details": results
    }
