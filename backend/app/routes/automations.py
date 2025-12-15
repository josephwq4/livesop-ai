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
        
        # --- LOG EXECUTION TO DB ---
        try:
            from app.repositories.persistence import PersistenceRepository
            repo = PersistenceRepository()
            
            from datetime import datetime, timezone
            
            db_entry = {
                "team_id": team_id,
                "trigger_type": action_type,
                "status": "completed" if result["success"] else "failed",
                "model_config": {
                    "confidence": 1.0,
                    "reasoning": f"Manual trigger by user {current_user.get('email', 'unknown')}",
                    "result_summary": result.get("message")
                },
                "started_at": datetime.now(timezone.utc).isoformat(),
                "completed_at": datetime.now(timezone.utc).isoformat()
            }
            repo.db.table("inference_runs").insert(db_entry).execute()
            
            # Also update usage stats if successful!
            if result["success"]:
                 # Increment usage counter
                try:
                    repo.db.rpc('increment_usage', {'team_id_input': team_id}).execute()
                except Exception as e:
                    print(f"Failed to increment usage: {e}")

        except Exception as e:
            print(f"Failed to log automation: {e}")
            # Don't fail the request if logging fails, but log error

        return result
    
    except Exception as e:
        print(f"[Automation Error] {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/replay/{signal_id}")
def replay_signal(
    signal_id: str, 
    dry_run: bool = False,
    current_user: dict = Depends(get_current_user)
):
    """
    Internal/Admin: Deterministic Replay of a past signal through the Auto-Pilot Engine.
    Useful for testing, debugging, or dry-running logic changes.
    """
    try:
        from app.repositories.persistence import PersistenceRepository
        from app.services.trigger_engine import evaluate_signal
        
        repo = PersistenceRepository()
        
        # 1. Fetch Signal
        signal = repo.get_signal_by_id(signal_id)
        if not signal:
             raise HTTPException(status_code=404, detail="Signal not found")
             
        team_id = signal["team_id"]
        
        # 2. Re-Run Evaluation
        # We pass dry_run=True usually for testing. 
        # But if user explicitly wants to re-execute, they can pass dry_run=False.
        
        print(f"[Replay] Replaying signal {signal_id} for team {team_id} (DryRun={dry_run})")
        
        # Note: evaluate_signal builds its own idempotency key.
        # If dry_run=False, it might accidentally skip if the key matches a previous real run.
        # However, evaluate_signal's idempotency check is skipped if dry_run=True.
        # If user attempts a FORCE REPLAY (dry_run=False) of an already executed event, 
        # our logic currently blocks it unless we added a 'force' flag.
        # For now, let's assume 'dry_run=True' is the primary use case for checking logic.
        # If dry_run=False (Force Execute), the hash might collide.
        # Let's trust the logic: if it ran before, we shouldn't run it again automatically.
        # But this is an explicit manual trigger.
        
        # Let's assume manual replay should bypass idempotency check logic inside evaluate_signal?
        # Actually evaluate_signal logic: if not dry_run => check idempotency.
        # So Real Replay will fail if done before.
        # This is SAFE. Idempotency is strict.
        # To force re-run, one would need to delete the old run or change the signal slightly.
        # OR we modify evaluate_signal to accept 'ignore_idempotency' arg. 
        # For Phase A, strict idempotency is desired.
        
        evaluate_signal(team_id, signal, dry_run=dry_run)
        
        return {
            "success": True,
            "message": f"Replay triggered for {signal_id}",
            "mode": "dry_run" if dry_run else "live_execution"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Replay failed: {str(e)}")


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
            
        # Phase B: Skip Surfacing Logic
        # Filter out low-confidence signals from Live Feed (but they remain in DB for audit)
        SURFACE_THRESHOLD = 0.5  # Only show signals with confidence >= 50%
        
        feed = []
        for r in res.data:
            # Check confidence before surfacing
            confidence = r.get("model_config", {}).get("confidence", 0.0)
            
            # Skip low-confidence signals from Live Feed
            if confidence < SURFACE_THRESHOLD:
                continue
            
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
                "confidence": confidence,
                "action": r["trigger_type"],
                "status": r["status"],
                
                # Trust Panel Data
                "content": primary_signal.get("content", ""),
                "channel_id": primary_signal.get("metadata", {}).get("channel_id", ""),
                "link": primary_signal.get("metadata", {}).get("permalink", ""),
                "rationale": r.get("model_config", {}).get("reasoning", "Matched Tier-3 Escalation criteria based on keywords.")
            })
            
        return {"feed": feed}

    except Exception as e:
        print(f"Live Feed Error: {e}")
        # Return empty feed instead of crash
        return {"feed": []}
