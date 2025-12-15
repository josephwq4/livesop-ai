import os
import json
from datetime import datetime, timezone
from typing import Dict, Any, Tuple
from app.repositories.persistence import PersistenceRepository
from app.services.automation_service import run_automation_logic
# Import OpenAI client (Assumes initialized in workflow_inference or reusable here)
from openai import OpenAI

# Init OpenAI (ensure key is available)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def _match_signal_to_nodes(signal_text: str, nodes: list) -> Tuple[Dict, float, str]:
    """
    Uses LLM to determine if the signal matches any auto-pilot enabled node.
    Returns: (matched_node, confidence_score, reasoning)
    """
    if not nodes:
        return None, 0.0, "No active nodes"

    # Filter only auto-pilot nodes
    candidates = [n for n in nodes if n.get("data", {}).get("auto_pilot")]
    if not candidates:
        return None, 0.0, "No auto-pilot nodes enabled"

    cand_descriptions = "\n".join([
        f"- Node ID: {n.get('id')} | Label: {n.get('data', {}).get('label')} | Desc: {n.get('data', {}).get('description')}" 
        for n in candidates
    ])

    prompt = f"""
    Analyze the incoming signal against the following workflow nodes.
    Determine if the signal explicitly triggers any of them with high confidence.
    
    Signal: "{signal_text}"
    
    Candidate Nodes:
    {cand_descriptions}
    
    Respond in JSON format:
    {{
        "match": true/false,
        "node_id": "step_id_or_null",
        "confidence": 0.0_to_1.0,
        "reasoning": "brief explanation"
    }}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o", # Use smart model for decision making
            messages=[{"role": "system", "content": "You are a deterministic workflow engine."}, {"role": "user", "content": prompt}],
            temperature=0.0,
            response_format={"type": "json_object"}
        )
        result = json.loads(response.choices[0].message.content)
        
        if result.get("match") and result.get("confidence") > 0.0:
            matched_node = next((n for n in candidates if n.get("id") == result.get("node_id")), None)
            return matched_node, result.get("confidence"), result.get("reasoning")
            
        return None, result.get("confidence", 0.0), result.get("reasoning", "No match found")
        
    except Exception as e:
        print(f"[Trigger AI Error] {e}")
        return None, 0.0, f"AI Error: {str(e)}"

def evaluate_signal(team_id: str, signal: Dict[str, Any]):
    """
    Phase 9 Hardening: Intelligent, Confidence-Gated Auto-Pilot Execution.
    """
    repo = PersistenceRepository()
    
    try:
        print(f"[Trigger] Evaluating signal for team {team_id}: {signal.get('text', '')[:30]}...")
        
        # 1. Fetch Workflow
        workflow = repo.get_active_workflow(team_id)
        if not workflow or not workflow.get("nodes"):
            print("[Trigger] No active workflow.")
            return

        # 2. Intelligent Match
        matched_node, confidence, reasoning = _match_signal_to_nodes(
            signal.get("text", ""), 
            workflow["nodes"]
        )
        
        # 3. Decision Gate (Default 0.9)
        THRESHOLD = 0.9
        should_execute = (matched_node is not None) and (confidence >= THRESHOLD)
        
        status = "skipped"
        if should_execute:
            status = "executing"
        elif matched_node:
            status = "rejected_low_confidence"
            
        # 4. Audit Log (START)
        # We record the "attempt" or decision even if rejected, providing visibility.
        run_entry = {
            "team_id": team_id,
            "trigger_type": "auto_pilot_evaluation",  # Distinguish from manual
            "status": "processing",
            "model_config": {
                "matched_node": matched_node.get("data", {}).get("label") if matched_node else None,
                "confidence": confidence,
                "reasoning": reasoning,
                "threshold": THRESHOLD,
                "signal_text": signal.get("text", "") # critical context
            },
            "started_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Only log significant events (matches or high-confidence rejections) 
        # to avoid flooding DB with "0% match" on every message?
        # Requirement: "Full Audit Trail". We log if there was *any* candidate consideration.
        if confidence > 0.1:
            res = repo.db.table("inference_runs").insert(run_entry).execute()
            run_id = res.data[0]["id"]
            
            # Link Signal
            # We assume signal has an ID in raw_signals. But we just ingested it in webhooks.
            # We need to look up signal ID or pass it. 
            # Ideally webhooks/ingest returns the ID. 
            # For now, we skip explicit link if we don't have the UUID handy, 
            # but we persist the text in model_config so it's visible.
        else:
            return # Ignore noise

        # 5. Execution (If Passed)
        if should_execute:
            node_data = matched_node.get("data", {})
            label = node_data.get("label", "").lower()
            
            # Determine Action Params
            action = "slack_notify"
            params = {"message": f"🤖 Auto-Pilot: Executed '{node_data.get('label')}' based on your workflow rules."}
            
            # Heuristic for Action Type (Refine this later to be config-driven)
            if any(x in label for x in ["jira", "ticket", "issue"]):
                action = "create_jira_ticket"
                params = {
                    "summary": f"[Auto] {node_data.get('label')}",
                    "description": f"Triggered by Signal: {signal.get('text')}\n\nReasoning: {reasoning}"
                }
            
            # Execute Service
            print(f"[Auto-Pilot] EXECUTING {action} (Conf: {confidence})")
            result = run_automation_logic(team_id, action, params)
            
            # 6. Update Audit Log (COMPLETE)
            repo.db.table("inference_runs").update({
                "status": "completed" if result["success"] else "failed",
                "trigger_type": action, # Update to actual action taken
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "model_config": {
                     # Preserve previous context
                     "matched_node": matched_node.get("data", {}).get("label"),
                     "confidence": confidence,
                     "reasoning": reasoning,
                     "threshold": THRESHOLD,
                     "signal_text": signal.get("text", ""),
                     "execution_result": result
                }
            }).eq("id", run_id).execute()
            
            # 7. Update Usage
            if result["success"]:
                 repo.db.rpc('increment_usage', {'team_id_input': team_id}).execute()
                 
        else:
            # Mark Low Confidence
             repo.db.table("inference_runs").update({
                "status": "skipped",
                "completed_at": datetime.now(timezone.utc).isoformat()
            }).eq("id", run_id).execute()
            print(f"[Auto-Pilot] Skipped. Confidence {confidence} < {THRESHOLD}")

    except Exception as e:
        print(f"[Trigger Engine Error] {e}")
