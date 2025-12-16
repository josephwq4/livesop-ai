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

from app.services.rag_service import RAGService

def _match_signal_to_nodes(signal_text: str, nodes: list, context_text: str = "") -> Tuple[Dict, float, str]:
    """
    Uses LLM to determine if the signal matches any auto-pilot enabled node.
    Returns: (matched_node, confidence_score, reasoning)
    """
    if not nodes:
        return None, 0.0, "No active nodes"

    # Filter only auto-pilot nodes
    candidates = [n for n in nodes if n.get("data", {}).get("auto_pilot") or n.get("auto_run_enabled")] # Check both flag locations
    if not candidates:
        return None, 0.0, "No auto-pilot nodes enabled"

    cand_descriptions = "\n".join([
        f"- Node ID: {n.get('id')} | Label: {n.get('data', {}).get('label')} | Desc: {n.get('data', {}).get('description')}" 
        for n in candidates
    ])

    prompt = f"""
    Analyze the incoming signal against the following workflow nodes.
    Determine if the signal explicitly triggers any of them with high confidence.
    
    Context from Knowledge Base (Use this to inform your decision):
    {context_text if context_text else 'No additional context available.'}
    
    Signal: "{signal_text}"
    
    Candidate Nodes:
    {cand_descriptions}
    
    Respond in JSON format:
    {{
        "match": true/false,
        "node_id": "step_id_or_null",
        "confidence": 0.0_to_1.0,
        "reasoning": "brief explanation citing context if relevant"
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

import hashlib

def evaluate_signal(team_id: str, signal: Dict[str, Any], dry_run: bool = False):
    """
    Phase 9 Hardening: Intelligent, Confidence-Gated Auto-Pilot Execution.
    Supports dry_run and idempotency.
    """
    repo = PersistenceRepository()
    
    try:
        signal_text = signal.get("text", "")
        # 0. Idempotency Check
        # Hash: team_id + source + external_id (if available) or text + timestamp
        
        raw_key = f"{team_id}:{signal.get('source')}:{signal.get('id')}:{signal_text}"
        idempotency_key = hashlib.sha256(raw_key.encode('utf-8')).hexdigest()
        
        # If it's a dry run, we ignore idempotency (allow replay)
        if not dry_run:
             if repo.check_idempotency_key(team_id, idempotency_key):
                 print(f"[Trigger] Duplicate event detected. Skipping. Key: {idempotency_key[:8]}")
                 return 
        
        print(f"[Trigger] Evaluating signal for team {team_id} (DryRun={dry_run}): {signal_text[:30]}...")
        
        # 1. Fetch Workflow
        workflow = repo.get_active_workflow(team_id)
        if not workflow or not workflow.get("nodes"):
            print("[Trigger] No active workflow.")
            return

        # 1.5 Fetch Context (RAG)
        context_docs = []
        context_text = ""
        try:
            rag = RAGService()
            context_docs = rag.search_context(team_id, signal_text, limit=3)
            if context_docs:
                context_text = "\n".join([f"- {d['content'][:500]} (Source: {d['metadata'].get('filename', 'Unknown')})" for d in context_docs])
                print(f"[Trigger] Found {len(context_docs)} relevant KB items.")
        except Exception as rag_err:
             print(f"[Trigger] RAG Error: {rag_err}")

        # 2. Intelligent Match
        matched_node, confidence, reasoning = _match_signal_to_nodes(
            signal_text, 
            workflow["nodes"],
            context_text
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
        run_entry = {
            "team_id": team_id,
            "trigger_type": "auto_pilot_evaluation", 
            "status": "processing",
            "model_config": {
                "matched_node": matched_node.get("data", {}).get("label") if matched_node else None,
                "confidence": confidence,
                "reasoning": reasoning,
                "threshold": THRESHOLD,
                "signal_text": signal_text,
                "dry_run": dry_run,
                "idempotency_key": idempotency_key,
                "context_sources": [{ 
                    "title": d['metadata'].get("filename", "Unknown"), 
                    "snippet": d['content'][:150],
                    "source_type": d['metadata'].get("source", "manual"),
                    "metadata": d['metadata']
                } for d in context_docs]
            },
            "started_at": datetime.now(timezone.utc).isoformat()
        }
        
        if confidence > 0.1:
            res = repo.db.table("inference_runs").insert(run_entry).execute()
            run_id = res.data[0]["id"]
        else:
            return # Ignore noise

        # 5. Execution (If Passed)
        if should_execute:
            # Phase B: Safety Gates
            # Check 1: Global Kill Switch
            global_enabled = repo.get_team_auto_pilot_status(team_id)
            if not global_enabled:
                print(f"[Auto-Pilot] BLOCKED: Global Auto-Pilot disabled for team {team_id}")
                repo.db.table("inference_runs").update({
                    "status": "skipped",
                    "completed_at": datetime.now(timezone.utc).isoformat(),
                    "model_config": {
                         "matched_node": matched_node.get("data", {}).get("label"),
                         "confidence": confidence,
                         "reasoning": reasoning,
                         "threshold": THRESHOLD,
                         "signal_text": signal_text,
                         "dry_run": dry_run,
                         "idempotency_key": idempotency_key,
                         "skip_reason": "global_auto_pilot_disabled"
                    }
                }).eq("id", run_id).execute()
                return
            
            # Check 2: Per-Node Auto-Run Flag
            node_id = matched_node.get("id")
            node_enabled = repo.get_node_auto_run_status(node_id)
            if not node_enabled:
                print(f"[Auto-Pilot] BLOCKED: Node {node_id} has Auto-Run disabled")
                repo.db.table("inference_runs").update({
                    "status": "skipped",
                    "completed_at": datetime.now(timezone.utc).isoformat(),
                    "model_config": {
                         "matched_node": matched_node.get("data", {}).get("label"),
                         "confidence": confidence,
                         "reasoning": reasoning,
                         "threshold": THRESHOLD,
                         "signal_text": signal_text,
                         "dry_run": dry_run,
                         "idempotency_key": idempotency_key,
                         "skip_reason": f"node_auto_run_disabled:{node_id}"
                    }
                }).eq("id", run_id).execute()
                return
            
            # Recheck Dry Run
            if dry_run:
                # Log simulated success
                repo.db.table("inference_runs").update({
                    "status": "completed", # "completed" implies success for the *run* (which was a dry-run check)
                    "completed_at": datetime.now(timezone.utc).isoformat(),
                    "model_config": {
                         "matched_node": matched_node.get("data", {}).get("label"),
                         "confidence": confidence,
                         "reasoning": reasoning,
                         "threshold": THRESHOLD,
                         "signal_text": signal_text,
                         "dry_run": True,
                         "idempotency_key": idempotency_key,
                         "execution_result": {"success": True, "message": "Dry Run: Logic Validated.", "simulated": True}
                    }
                }).eq("id", run_id).execute()
                print(f"[Auto-Pilot] Dry Run Passed. Action would be executed.")
                return

            node_data = matched_node.get("data", {})
            label = node_data.get("label", "").lower()
            
            # Determine Action Params
            action = "slack_notify"
            params = {"message": f"🤖 Auto-Pilot: Executed '{node_data.get('label')}' based on your workflow rules."}
            
            if any(x in label for x in ["jira", "ticket", "issue"]):
                action = "create_jira_ticket"
                params = {
                    "summary": f"[Auto] {node_data.get('label')}",
                    "description": f"Triggered by Signal: {signal_text}\n\nReasoning: {reasoning}"
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
                     "matched_node": matched_node.get("data", {}).get("label"),
                     "confidence": confidence,
                     "reasoning": reasoning,
                     "threshold": THRESHOLD,
                     "signal_text": signal_text,
                     "dry_run": False,
                     "idempotency_key": idempotency_key,
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
