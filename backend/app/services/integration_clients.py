import os
import requests
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

# LAZY LOADING PATTERN:
# All heavy external libraries (slack_sdk, jira, google) must be imported INSIDE the function.
# This prevents specific library issues (version conflict, C-extension failure) from crashing the entire backend boot.

def fetch_slack_events(token: str, channel_id: str) -> List[Dict]:
    """Fetches valid messages from Slack for context awareness"""
    try:
        from slack_sdk import WebClient
        from slack_sdk.errors import SlackApiError
        
        client = WebClient(token=token)
        
        # 1. Get History
        try:
            result = client.conversations_history(channel=channel_id, limit=50)
            messages = result.get("messages", [])
            valid_msgs = []
            
            for msg in messages:
                if "subtype" in msg: continue # Skip system messages
                valid_msgs.append({
                    "id": msg.get("ts"),
                    "text": msg.get("text", ""),
                    "user": msg.get("user", "unknown"),
                    "timestamp": datetime.fromtimestamp(float(msg.get("ts", 0)), timezone.utc).isoformat(),
                    "source": "slack"
                })
            return valid_msgs
            
        except SlackApiError as e:
            print(f"Slack API Error: {e}")
            return []
            
    except ImportError:
        print("Slack SDK not installed")
        return []
    except Exception as e:
        print(f"Slack Client Error: {e}")
        return []

def fetch_jira_issues(api_key: str, project: str, email: str, server: str) -> List[Dict]:
    """Fetches recent Jibra issues"""
    try:
        from jira import JIRA
        
        options = {"server": server}
        jira_client = JIRA(options, basic_auth=(email, api_key))
        
        issues = jira_client.search_issues(f"project={project} ORDER BY created DESC", maxResults=20)
        results = []
        for issue in issues:
            results.append({
                "id": issue.key,
                "text": f"{issue.fields.summary} - {issue.fields.description or ''}",
                "user": issue.fields.reporter.displayName if issue.fields.reporter else "unknown",
                "timestamp": issue.fields.created,
                "source": "jira",
                "status": issue.fields.status.name
            })
        return results
        
    except Exception as e:
        print(f"Jira Error: {e}")
        return []

def fetch_gmail_threads(credentials: Any, label: str='INBOX') -> List[Dict]:
    """Stub for Gmail (Requires complex auth flow)"""
    return []

def send_slack_message(token: str, channel_id: str, text: str):
    """Sends a message back to Slack"""
    try:
        from slack_sdk import WebClient
        client = WebClient(token=token)
        client.chat_postMessage(channel=channel_id, text=text)
        return True
    except Exception as e:
        print(f"Slack Send Error: {e}")
        return False
