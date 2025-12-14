from app.repositories.persistence import PersistenceRepository
from app.services.automation_service import run_automation_logic
from typing import Dict, Any

def evaluate_signal(team_id: str, signal: Dict[str, Any]):
    """
    Evaluates a new signal against the active workflow to trigger auto-pilot nodes.
    """
    try:
        print(f"[Trigger] Evaluating signal for team {team_id}: {signal.get('text', '')[:30]}...")
        
        repo = PersistenceRepository()
        workflow = repo.get_active_workflow(team_id)
        
        if not workflow or not workflow.get("nodes"):
            return
            
        signal_text = signal.get("text", "").lower()
        
        for node in workflow["nodes"]:
            # Data structure from _assemble_workflow_graph matches node["data"]
            data = node.get("data", {})
            
            is_auto = data.get("auto_pilot") or False
            
            if is_auto:
                node_label = data.get("label", "").lower()
                
                # Heuristic: Match if signal text explicitly mentions the node label
                # In a real system, we'd use Vector Similarity > Threshold
                if node_label and node_label in signal_text:
                    print(f"[Auto-Pilot] MATCHED Node: {data.get('label')}. Executing...")
                    
                    # Determine Action based on refined heuristic or metadata
                    action = "slack_notify"
                    params = {"message": f"🤖 Auto-Pilot Executed: '{data.get('label')}' triggered by incoming signal."}
                    
                    # Detect Jira Intent
                    if any(x in node_label for x in ["jira", "ticket", "issue", "bug", "task"]):
                        action = "create_jira_ticket"
                        params = {
                            "summary": f"[Auto] {data.get('label')}",
                            "description": f"Triggered automatically by signal:\n{signal.get('text')}"
                        }
                    
                    # Execute
                    run_automation_logic(team_id, action, params)

    except Exception as e:
        print(f"[Trigger Engine Error] {e}")
