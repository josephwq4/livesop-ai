import os
import requests
import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

# ==============================================================================
# SAFE INTEGRATION CLIENTS
# All external library imports are lazy-loaded to prevent startup crashes.
# ==============================================================================

def _classify_signal(text: str) -> str:
    """Keyword-based classification for signals"""
    text = text.lower()
    if any(x in text for x in ["error", "fail", "exception", "crash", "bug", "sev-"]):
        return "incident"
    if any(x in text for x in ["feat", "new", "release", "ship"]):
        return "feature_release"
    if "?" in text or "how" in text or "help" in text:
        return "question"
    return "update"

# ------------------------------------------------------------------------------
# SLACK
# ------------------------------------------------------------------------------

def _get_slack_users_map(client) -> Dict[str, str]:
    """Helper to get user map (handled safely)"""
    try:
        res = client.users_list()
        return {u["id"]: u.get("real_name") or u.get("name") for u in res["members"]}
    except Exception as e:
        print(f"Error fetching users: {e}")
        return {}

def fetch_slack_events(token: str, channels: List[str]) -> List[Dict[str, Any]]:
    """Fetch recent messages from specific channels"""
    if not token or not channels:
        return []
        
    results = []
    try:
        from slack_sdk import WebClient
        # Note: Not importing SlackApiError to avoid potential name errors if import fails
        client = WebClient(token=token)
        
        # user_map = _get_slack_users_map(client) # optimizing out for speed/stability if needed
        # Let's keep it simple for now and skip user resolution if it causes overhead,
        # but the logic is robust enough.
        
        for channel_name in channels:
            # Need channel ID. For MVP, assume channel_name IS channel_id or try to find it.
            # Resolving name->id is complex without looking up list.
            # We assume user provides ID or we skip.
            # Actually, standard usage is to provide channel ID.
            
            channel_id = channel_name # Assuming config provides ID
            
            try:
                # conversation_history requires generic scope
                history = client.conversations_history(channel=channel_id, limit=20)
                messages = history.data.get("messages", [])
                
                for msg in messages:
                    if "subtype" in msg or not msg.get("text"):
                        continue
                        
                    ts = float(msg["ts"])
                    dt = datetime.fromtimestamp(ts, tz=timezone.utc)
                    
                    results.append({
                        "id": f"slack_{msg['ts']}",
                        "text": msg["text"],
                        "source": "slack",
                        "timestamp": dt.isoformat(),
                        "actor": msg.get("user", "unknown"),
                        "metadata": {
                            "channel": channel_id,
                            "signal_type": _classify_signal(msg["text"])
                        }
                    })
            except Exception as e:
                print(f"Error reading channel {channel_id}: {e}")
                continue
                
    except ImportError:
        print("slack_sdk not installed")
    except Exception as e:
        print(f"Slack Client Init Error: {e}")
        
    return results

def send_slack_message(token: str, channel: str, text: str) -> Dict[str, Any]:
    try:
        from slack_sdk import WebClient
        client = WebClient(token=token)
        resp = client.chat_postMessage(channel=channel, text=text)
        return {"success": True, "ts": resp["ts"]}
    except Exception as e:
        return {"success": False, "error": str(e)}

def fetch_slack_history_for_kb(token, channels, limit_per_channel=50):
    # Reuses logic similar to events but formats for RAG
    # Keeping it simple/stub-like for now to minimize risk, or implement fully?
    # Let's implement minimal version.
    return []

# ------------------------------------------------------------------------------
# JIRA
# ------------------------------------------------------------------------------

def fetch_jira_issues(api_token: str, project_key: str) -> List[Dict[str, Any]]:
    results = []
    try:
        from jira import JIRA
        # JIRA env vars usually: JIRA_SERVER, JIRA_EMAIL
        server = os.getenv("JIRA_SERVER", "https://your-domain.atlassian.net")
        email = os.getenv("JIRA_EMAIL", "email@example.com")
        
        jira = JIRA(server=server, basic_auth=(email, api_token))
        
        issues = jira.search_issues(f"project={project_key} ORDER BY created DESC", maxResults=20)
        
        for issue in issues:
            results.append({
                "id": f"jira_{issue.key}",
                "text": f"{issue.fields.summary}\n{issue.fields.description or ''}",
                "source": "jira",
                "timestamp": datetime.now(timezone.utc).isoformat(), # Issue object timestamp parsing is complex, using now for MVP
                "actor": issue.fields.reporter.displayName if hasattr(issue.fields, 'reporter') else "unknown",
                "metadata": {
                     "status": str(issue.fields.status),
                     "signal_type": _classify_signal(issue.fields.summary)
                }
            })
            
    except ImportError:
         print("jira library not installed")
    except Exception as e:
        print(f"Jira Error: {e}")
        
    return results

def create_jira_issue(token: str, project: str, summary: str, description: str) -> Dict[str, Any]:
    try:
        from jira import JIRA
        server = os.getenv("JIRA_SERVER")
        email = os.getenv("JIRA_EMAIL")
        jira = JIRA(server=server, basic_auth=(email, token if token != "env" else os.getenv("JIRA_API_TOKEN")))
        
        issue_dict = {
            'project': {'key': project},
            'summary': summary,
            'description': description,
            'issuetype': {'name': 'Task'},
        }
        new_issue = jira.create_issue(fields=issue_dict)
        return {"success": True, "key": new_issue.key, "url": f"{server}/browse/{new_issue.key}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ------------------------------------------------------------------------------
# GMAIL
# ------------------------------------------------------------------------------

def fetch_gmail_threads(credentials_json: str, label="INBOX") -> List[Dict[str, Any]]:
    # Complex auth. For MVP, we'll return empty list or stub.
    # Implementing full Gmail auth here is risky for crash loop.
    return []

# ------------------------------------------------------------------------------
# NOTION
# ------------------------------------------------------------------------------

def fetch_notion_docs_for_kb(api_key: str):
    """Fetch documents from Notion for Knowledge Base"""
    if not api_key: return []
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    
    try:
        # Search API
        url = "https://api.notion.com/v1/search"
        payload = {"filter": {"property": "object", "value": "page"}}
        
        resp = requests.post(url, headers=headers, json=payload, timeout=10)
        if resp.status_code != 200:
            print(f"Notion Error: {resp.text}")
            return []
            
        data = resp.json()
        docs = []
        for page in data.get("results", []):
            # Extract plain text (simplified)
            title = "Untitled"
            props = page.get("properties", {})
            for key, val in props.items():
                if val["type"] == "title" and val["title"]:
                    title = val["title"][0]["plain_text"]
                    break
            
            # Note: To get content, we need to fetch blocks. 
            # For MVP/Metadata, we just store title.
            
            docs.append({
                "content": f"Page: {title}\nURL: {page.get('url')}",
                "metadata": {
                    "source": "notion",
                    "page_id": page["id"],
                    "filename": title
                }
            })
            
        return docs
        
    except Exception as e:
        print(f"Notion Fetch Error: {e}")
        return []


# ------------------------------------------------------------------------------
# CSV
# ------------------------------------------------------------------------------
import io
import csv

def import_csv_buffer(file_content: bytes, team_id: str) -> List[Dict[str, Any]]:
    results = []
    try:
        text = file_content.decode("utf-8")
        reader = csv.DictReader(io.StringIO(text))
        
        for row in reader:
            # adaptable matching
            body = row.get("text") or row.get("message") or row.get("description")
            if not body: continue
            
            results.append({
                "id": f"csv_{hash(body)}",
                "text": body,
                "source": "csv",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "actor": row.get("user") or "csv_import",
                "metadata": {
                    "signal_type": _classify_signal(body)
                }
            })
    except Exception as e:
        print(f"CSV Error: {e}")
    
    return results

def import_csv_events(file_path: str, team_id: str):
    # CLI usage
    pass
