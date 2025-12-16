from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, BackgroundTasks
from typing import List
from app.services.integration_clients import (
    fetch_slack_events,
    fetch_jira_issues,
    fetch_gmail_threads,
    import_csv_events,
    import_csv_buffer,
    fetch_slack_history_for_kb,
    fetch_notion_docs_for_kb
)
from app.services.rag_service import RAGService
from app.models.workflow import Event
from app.dependencies.auth import get_current_user
from app.repositories.persistence import PersistenceRepository
import tempfile
import os
import io

router = APIRouter(tags=["integrations"])


def _get_repo_and_team(current_user: dict):
    """Helper to resolve repo and team from auth"""
    repo = PersistenceRepository()
    user_id = current_user.get("sub")
    # Consistent team resolution logic
    real_team_id = repo.get_or_create_team(f"Team {user_id[:4]}", user_id)
    return repo, real_team_id


@router.get("/slack")
def get_slack_events(
    token: str, 
    channels: str,
    current_user: dict = Depends(get_current_user)
):
    """Fetch and INGEST events from Slack channels"""
    try:
        repo, team_id = _get_repo_and_team(current_user)

        # Fallback to env var if token is empty or placeholder
        if not token or len(token) < 10 or token == "env":
            token = os.getenv("SLACK_TOKEN", "")

        channel_list = channels.split(",")
        events = fetch_slack_events(token, channel_list)
        
        # Ingest into DB
        if events:
            repo.ingest_signals(team_id, events)

        return {
            "success": True,
            "source": "slack",
            "count": len(events),
            "events": events # Optional: truncate if too large
        }
    except Exception as e:
        import traceback
        print("❌ [ROUTE ERROR] /integrations/slack failed:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error fetching Slack events: {str(e)}")


@router.get("/jira")
def get_jira_issues(
    api_key: str, 
    project: str,
    current_user: dict = Depends(get_current_user)
):
    """Fetch and INGEST issues from Jira project"""
    try:
        repo, team_id = _get_repo_and_team(current_user)

        issues = fetch_jira_issues(api_key, project)
        
        # Ingest into DB
        if issues:
            repo.ingest_signals(team_id, issues)

        return {
            "success": True,
            "source": "jira",
            "count": len(issues),
            "issues": issues
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching Jira issues: {str(e)}")


@router.get("/gmail")
def get_gmail_threads(
    credentials: str, 
    label: str = "INBOX",
    current_user: dict = Depends(get_current_user)
):
    """Fetch and INGEST email threads from Gmail"""
    try:
        repo, team_id = _get_repo_and_team(current_user)

        threads = fetch_gmail_threads(credentials, label)
        
        # Ingest into DB
        if threads:
            repo.ingest_signals(team_id, threads)

        return {
            "success": True,
            "source": "gmail",
            "count": len(threads),
            "threads": threads
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching Gmail threads: {str(e)}")


@router.post("/csv/upload")
async def upload_csv(
    team_id: str = None, # Optional: kept for API compat but ignored/verified
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload and INGEST events from CSV file"""
    try:
        repo, real_team_id = _get_repo_and_team(current_user)

        # Read file content
        content = await file.read()
        
        # Import events from memory using io.BytesIO
        events = import_csv_buffer(content, real_team_id)
        
        # Ingest into DB
        if events:
            repo.ingest_signals(real_team_id, events)
        
        return {
            "success": True,
             "source": "csv",
            "filename": file.filename,
            "count": len(events),
            "events": events
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error importing CSV: {str(e)}")


@router.post("/{team_id}/slack/sync")
async def sync_slack_knowledge(team_id: str, background_tasks: BackgroundTasks, current_user: dict = Depends(get_current_user)):
    """Async trigger to sync Slack history into Knowledge Base"""
    
    # 1. Resolve Team
    rag_service = RAGService()
    user_id = current_user.get("sub")
    real_team_id = rag_service.repo.get_or_create_team(f"Team {user_id[:4]}", user_id)
    
    # 2. Get Credentials (MVP: Env Vars)
    token = os.getenv("SLACK_TOKEN")
    channels_env = os.getenv("SLACK_CHANNELS", "general")
    channels = [c.strip() for c in channels_env.split(",")]
    
    if not token or token == "env":
        return {"success": False, "message": "Slack not configured"}

    # 3. Define Task
    def _sync_task(t_id, tok, chans):
        print(f"[Sync] Starting Slack Sync for {t_id}...")
        try:
            items = fetch_slack_history_for_kb(tok, chans, limit_per_channel=50) 
            if items:
                count = rag_service.add_documents_batch(t_id, items)
                print(f"[Sync] Slack Sync Complete. Ingested {count} items.")
            else:
                print("[Sync] No items found.")
        except Exception as e:
            print(f"[Sync] Error: {e}")

    background_tasks.add_task(_sync_task, real_team_id, token, channels)
    
    return {"success": True, "message": "Slack sync started in background"}


@router.post("/{team_id}/notion/sync")
async def sync_notion_knowledge(team_id: str, background_tasks: BackgroundTasks, current_user: dict = Depends(get_current_user)):
    """Async trigger to sync Notion pages into Knowledge Base"""
    
    rag_service = RAGService()
    user_id = current_user.get("sub")
    real_team_id = rag_service.repo.get_or_create_team(f"Team {user_id[:4]}", user_id)
    
    # Env var for MVP
    api_key = os.getenv("NOTION_API_KEY") 
    
    if not api_key:
        return {"success": False, "message": "Notion not configured"}

    def _sync_task(t_id, key):
        print(f"[Sync] Starting Notion Sync for {t_id}...")
        try:
             items = fetch_notion_docs_for_kb(key)
             if items:
                 count = rag_service.add_documents_batch(t_id, items)
                 print(f"[Sync] Notion Sync Complete. Ingested {count} items.")
             else:
                 print("[Sync] No Notion items found.")
        except Exception as e:
            print(f"[Sync] Notion Error: {e}")

    background_tasks.add_task(_sync_task, real_team_id, api_key)
    
    return {"success": True, "message": "Notion sync started in background"}
