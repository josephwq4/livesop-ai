from typing import List, Dict, Any

def fetch_all_events(team_id: str) -> List[Dict[str, Any]]:
    return []

def fetch_slack_events(token: str, channels: List[str]) -> List[Dict[str, Any]]:
    return []

def fetch_jira_issues(api_key: str, project: str) -> List[Dict[str, Any]]:
    return []

def fetch_gmail_threads(credentials_json: str, label: str) -> List[Dict[str, Any]]:
    return []

def import_csv_buffer(content: bytes, team_id: str) -> List[Dict[str, Any]]:
    return []

def import_csv_events(file_path: str, team_id: str) -> List[Dict[str, Any]]:
    return []

def send_slack_message(token: str, channel: str, text: str) -> Dict[str, Any]:
    return {"success": True}

def create_jira_issue(api_key: str, project_key: str, summary: str, description: str, issue_type: str = "Task") -> Dict[str, Any]:
    return {"success": True, "key": "STUB-123", "url": "http://stub"}

def fetch_slack_history_for_kb(token: str, channels: List[str], limit_per_channel: int = 50) -> List[Dict]:
    return []

def fetch_notion_docs_for_kb(api_key: str) -> List[Dict]:
    return []

def _classify_signal(text: str) -> str:
    return "unknown"
