from fastapi import APIRouter, Request, HTTPException, BackgroundTasks, Header
from app.services.integration_clients import _classify_signal
from app.repositories.persistence import PersistenceRepository
import os
import json
import hmac
import hashlib
import time
from datetime import datetime

router = APIRouter(tags=["webhooks"])

async def process_slack_event(event: dict, slack_team_id: str):
    """Process Slack event in background"""
    try:
        # Filter: Only messages, no bot messages
        if event.get("type") != "message" or event.get("subtype"):
             return 
        
        if event.get("bot_id"):
             return 
             
        repo = PersistenceRepository()
        
        # Resolve Team ID (MVP Strategy: Pick the first available team in DB)
        # In a real SaaS, we would look up the team that installed the Slack App via slack_team_id.
        team_res = repo.db.table("teams").select("id").limit(1).execute()
        if not team_res.data:
            print("❌ [Webhook] No teams found in DB. Dropping signal.")
            return
            
        target_team_id = team_res.data[0]["id"]

        text = event.get("text", "")
        actor = event.get("user", "unknown") 
        ts = event.get("ts")
        channel = event.get("channel")
        
        # Construct Signal
        new_signal = {
            "id": f"slack_{ts}",
            "text": text,
            "source": "slack",
            "timestamp": datetime.fromtimestamp(float(ts)).isoformat(),
            "actor": actor,
            "metadata": {
                "channel": channel,
                "signal_type": _classify_signal(text),
                "slack_event_id": event.get("client_msg_id"),
                "slack_team_id": slack_team_id
            }
        }
        
        # Insert
        repo.ingest_signals(target_team_id, [new_signal])
        print(f"✅ [Webhook] Ingested signal from {actor}: {text[:30]}... -> Team {target_team_id}")
        
    except Exception as e:
        print(f"❌ [Webhook] Error processing event: {e}")


@router.post("/slack")
async def slack_webhook(request: Request, background_tasks: BackgroundTasks):
    body_bytes = await request.body()
    body_str = body_bytes.decode("utf-8")
    
    # 1. Verify Signature
    timestamp = request.headers.get("X-Slack-Request-Timestamp")
    signature = request.headers.get("X-Slack-Signature")
    signing_secret = os.getenv("SLACK_SIGNING_SECRET")
    
    if signing_secret:
        if not timestamp or not signature:
             raise HTTPException(status_code=403, detail="Missing Headers")
             
        # Check timestamp age (replay attack)
        if abs(time.time() - int(timestamp)) > 60 * 5:
            raise HTTPException(status_code=403, detail="Request too old")
            
        basestring = f"v0:{timestamp}:{body_str}".encode('utf-8')
        my_signature = "v0=" + hmac.new(
            signing_secret.encode('utf-8'), 
            basestring, 
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(my_signature, signature):
             raise HTTPException(status_code=403, detail="Invalid Signature")
    else:
        print("⚠️ [Webhook] SLACK_SIGNING_SECRET missing. Skipping verification.")

    # 2. Parse Body
    try:
        payload = json.loads(body_str)
    except json.JSONDecodeError:
         raise HTTPException(status_code=400, detail="Invalid JSON")

    # 3. Handle Challenge (Handshake)
    if payload.get("type") == "url_verification":
        return {"challenge": payload.get("challenge")}

    # 4. Handle Event Callback
    if payload.get("type") == "event_callback":
        event = payload.get("event", {})
        # Offload processing
        background_tasks.add_task(process_slack_event, event, payload.get("team_id"))
        return {"status": "ok"}
        
    return {"status": "ignored"}
