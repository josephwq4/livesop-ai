import os
from typing import Dict, Any, List
from datetime import datetime
import json


class AutomationRunner:
    """Handles execution of workflow automations"""
    
    def __init__(self):
        self.automation_log = []
    
    def log_automation(self, team_id: str, workflow_id: str, status: str, details: Dict[str, Any]):
        """Log automation execution"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "team_id": team_id,
            "workflow_id": workflow_id,
            "status": status,
            "details": details
        }
        self.automation_log.append(log_entry)
        print(f"[AUTOMATION LOG] {json.dumps(log_entry, indent=2)}")
    
    def run_automation(self, team_id: str, workflow_id: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a workflow automation"""
        print(f"Running automation for workflow {workflow_id} in team {team_id}")
        
        if parameters is None:
            parameters = {}
        
        # Simulate automation execution
        # In production, this would:
        # 1. Fetch workflow definition
        # 2. Execute each step
        # 3. Handle errors and retries
        # 4. Send notifications
        
        try:
            # Mock automation steps
            steps_executed = [
                {
                    "step_id": "step_1",
                    "action": "create_jira_ticket",
                    "status": "success",
                    "result": {"ticket_id": "PROJ-456"}
                },
                {
                    "step_id": "step_2",
                    "action": "send_slack_notification",
                    "status": "success",
                    "result": {"message_id": "msg_123"}
                },
                {
                    "step_id": "step_3",
                    "action": "update_spreadsheet",
                    "status": "success",
                    "result": {"row_updated": 5}
                }
            ]
            
            result = {
                "success": True,
                "workflow_id": workflow_id,
                "team_id": team_id,
                "executed_at": datetime.now().isoformat(),
                "steps_executed": steps_executed,
                "parameters": parameters
            }
            
            self.log_automation(team_id, workflow_id, "success", result)
            return result
            
        except Exception as e:
            error_result = {
                "success": False,
                "workflow_id": workflow_id,
                "team_id": team_id,
                "error": str(e),
                "executed_at": datetime.now().isoformat()
            }
            
            self.log_automation(team_id, workflow_id, "failed", error_result)
            return error_result
    
    def get_automation_history(self, team_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get automation execution history for a team"""
        team_logs = [
            log for log in self.automation_log
            if log["team_id"] == team_id
        ]
        return team_logs[-limit:]
    
    def schedule_automation(self, team_id: str, workflow_id: str, schedule: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Schedule a recurring automation"""
        # In production, this would integrate with a task scheduler like Celery or APScheduler
        scheduled_automation = {
            "automation_id": f"auto_{team_id}_{workflow_id}_{int(datetime.now().timestamp())}",
            "team_id": team_id,
            "workflow_id": workflow_id,
            "schedule": schedule,  # e.g., "daily", "weekly", "0 9 * * *" (cron)
            "parameters": parameters or {},
            "created_at": datetime.now().isoformat(),
            "status": "scheduled"
        }
        
        print(f"Scheduled automation: {json.dumps(scheduled_automation, indent=2)}")
        return scheduled_automation


# Global automation runner instance
automation_runner = AutomationRunner()


def run_automation(team_id: str, workflow_id: str, parameters: Dict[str, Any] = None) -> bool:
    """Execute automation (legacy function for compatibility)"""
    result = automation_runner.run_automation(team_id, workflow_id, parameters)
    return result["success"]
