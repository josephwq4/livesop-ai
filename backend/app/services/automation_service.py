from typing import Dict, Any
import os
from app.services.integration_clients import send_slack_message, create_jira_issue

def run_automation_logic(team_id: str, action_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Core automation execution logic, decoupled from HTTP context"""
    print(f"[Automation Service] Executing {action_type} for team {team_id}")
    
    try:
        if action_type == "create_jira_ticket":
            # Defaults
            project = params.get("project") or os.getenv("JIRA_PROJECT", "PROJ")
            summary = params.get("summary", "New Task from LiveSOP")
            desc = params.get("description", "Created via LiveSOP Automation")
            
            # Execute
            res = create_jira_issue("env", project, summary, desc)
            if res["success"]:
                return {
                    "success": True, 
                    "message": f"Created Jira Ticket {res['key']}",
                    "url": res.get("url")
                }
            else:
                return {"success": False, "message": res.get("error", "Jira Error")}

        elif action_type == "slack_notify":
            channel = params.get("channel") or os.getenv("SLACK_CHANNELS", "general").split(",")[0]
            text = params.get("message", "Hello from LiveSOP")
            token = os.getenv("SLACK_TOKEN", "")
            
            res = send_slack_message(token, channel, text)
            if res["success"]:
                return {"success": True, "message": "Slack message sent"}
            else:
                 return {"success": False, "message": res.get("error", "Slack Error")}

        return {"success": False, "message": f"Unsupported action: {action_type}"}
        
    except Exception as e:
        print(f"[Automation Service Error] {e}")
        return {"success": False, "message": str(e)}
