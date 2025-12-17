from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, List
from app.dependencies.auth import get_current_user
from app.services.integration_clients import fetch_slack_events, fetch_jira_issues

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
