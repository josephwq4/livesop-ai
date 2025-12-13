from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List
from app.services.integration_clients import (
    fetch_slack_events,
    fetch_jira_issues,
    fetch_gmail_threads,
    import_csv_events,
    import_csv_buffer
)
from app.models.workflow import Event
import tempfile
import os
import io

router = APIRouter(tags=["integrations"])


@router.get("/slack")
def get_slack_events(token: str, channels: str):
    """Fetch events from Slack channels"""
    try:
        # Fallback to env var if token is empty or placeholder
        if not token or len(token) < 10 or token == "env":
            token = os.getenv("SLACK_TOKEN", "")

        channel_list = channels.split(",")
        events = fetch_slack_events(token, channel_list)
        return {
            "success": True,
            "source": "slack",
            "count": len(events),
            "events": events
        }
    except Exception as e:
        import traceback
        print("❌ [ROUTE ERROR] /integrations/slack failed:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error fetching Slack events: {str(e)}")


@router.get("/jira")
def get_jira_issues(api_key: str, project: str):
    """Fetch issues from Jira project"""
    try:
        issues = fetch_jira_issues(api_key, project)
        return {
            "success": True,
            "source": "jira",
            "count": len(issues),
            "issues": issues
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching Jira issues: {str(e)}")


@router.get("/gmail")
def get_gmail_threads(credentials: str, label: str = "INBOX"):
    """Fetch email threads from Gmail"""
    try:
        threads = fetch_gmail_threads(credentials, label)
        return {
            "success": True,
            "source": "gmail",
            "count": len(threads),
            "threads": threads
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching Gmail threads: {str(e)}")


@router.post("/csv/upload")
async def upload_csv(team_id: str, file: UploadFile = File(...)):
    """Upload and import events from CSV file"""
    try:
        # Read file content
        content = await file.read()
        
        # Import events from memory using io.BytesIO
        events = import_csv_buffer(content, team_id)
        
        return {
            "success": True,
             "source": "csv",
            "filename": file.filename,
            "count": len(events),
            "events": events
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error importing CSV: {str(e)}")


@router.get("/test")
def test_integrations():
    """Test endpoint to verify integrations are working"""
    return {
        "status": "ok",
        "message": "Integrations API is running",
        "available_integrations": ["slack", "jira", "gmail", "csv"]
    }
