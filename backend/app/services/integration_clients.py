import os
import requests
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

# LAZY LOADING PATTERN:
# All heavy external libraries (slack_sdk, jira, google) must be imported INSIDE the function.

def fetch_slack_events(token: str, channel_id: str) -> List[Dict]:
    """Fetches valid messages from Slack for context awareness"""
    try:
        from slack_sdk import WebClient
        from slack_sdk.errors import SlackApiError
        
        client = WebClient(token=token)
        try:
            result = client.conversations_history(channel=channel_id, limit=50)
            messages = result.get("messages", [])
            valid_msgs = []
            for msg in messages:
                if "subtype" in msg: continue 
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
    return []

def send_slack_message(token: str, channel_id: str, text: str):
    try:
        from slack_sdk import WebClient
        client = WebClient(token=token)
        client.chat_postMessage(channel=channel_id, text=text)
        return True
    except Exception as e:
        print(f"Slack Send Error: {e}")
        return False

def fetch_all_events(team_id: str) -> List[Dict]:
    """
    Aggregator function used by Workflow Inference.
    Currently stubbed to return empty list or use basic Env Vars if available.
    """
    # For MVP, we can check basic env vars or just return empty
    # Logic: We can't fetch real events because we don't have the token passed in here.
    # In Phase 2, this function should query 'channel_configs' table to get tokens.
    # For Checkpoint Alpha+, return empty to be safe.
    return []
