from typing import List, Dict, Any

def _classify_signal(text): return "update"
def fetch_slack_events(t, c): return []
def send_slack_message(t, c, msg): return {"success": True}
def fetch_slack_history_for_kb(t, c, l=50): return []
def fetch_jira_issues(t, p): return []
def create_jira_issue(t, p, s, d): return {"success": True, "key": "MOCK"}
def fetch_gmail_threads(c, l="INBOX"): return []
def fetch_notion_docs_for_kb(k): return []
def import_csv_buffer(c, t): return []
def import_csv_events(f, t): pass
