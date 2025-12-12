import os
from typing import List, Dict, Any
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from jira import JIRA
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import pandas as pd
from datetime import datetime


def fetch_all_events(team_id: str) -> List[Dict[str, Any]]:
    """Combine events from all integrated sources"""
    all_events = []
    
    # Fetch from different sources
    # In production, these would use team-specific credentials from database
    try:
        slack_events = fetch_slack_events(os.getenv("SLACK_TOKEN", ""), ["general"])
        all_events.extend(slack_events)
    except Exception as e:
        print(f"Error fetching Slack events: {e}")
    
    try:
        jira_events = fetch_jira_issues(os.getenv("JIRA_API_KEY", ""), os.getenv("JIRA_PROJECT", ""))
        all_events.extend(jira_events)
    except Exception as e:
        print(f"Error fetching Jira issues: {e}")
    
    try:
        gmail_events = fetch_gmail_threads(os.getenv("GMAIL_CREDENTIALS", ""), "INBOX")
        all_events.extend(gmail_events)
    except Exception as e:
        print(f"Error fetching Gmail threads: {e}")
    
    # Add team_id to all events
    for event in all_events:
        event["team_id"] = team_id
    
    return all_events


def fetch_slack_events(token: str, channels: List[str]) -> List[Dict[str, Any]]:
    """Fetch messages from Slack channels"""
    if not token:
        # Return mock data for MVP
        return [
            {
                "id": "slack_1",
                "text": "Alice: Started working on the new feature deployment",
                "timestamp": datetime.now().isoformat(),
                "actor": "Alice",
                "source": "slack",
                "metadata": {"channel": "general"}
            },
            {
                "id": "slack_2",
                "text": "Bob: Reviewed the PR and approved it",
                "timestamp": datetime.now().isoformat(),
                "actor": "Bob",
                "source": "slack",
                "metadata": {"channel": "general"}
            }
        ]
    
    try:
        client = WebClient(token=token)
        events = []
        
        for channel in channels:
            response = client.conversations_history(channel=channel, limit=50)
            for message in response["messages"]:
                events.append({
                    "id": f"slack_{message.get('ts')}",
                    "text": message.get("text", ""),
                    "timestamp": message.get("ts", ""),
                    "actor": message.get("user", "unknown"),
                    "source": "slack",
                    "metadata": {"channel": channel}
                })
        
        return events
    except SlackApiError as e:
        print(f"Slack API Error: {e}")
        return []


def fetch_jira_issues(api_key: str, project: str) -> List[Dict[str, Any]]:
    """Fetch issues from Jira project"""
    if not api_key or not project:
        # Return mock data for MVP
        return [
            {
                "id": "jira_1",
                "text": "PROJ-123: Bug fix - Login page not responsive on mobile",
                "timestamp": datetime.now().isoformat(),
                "actor": "Carol",
                "source": "jira",
                "metadata": {"status": "In Progress", "priority": "High"}
            },
            {
                "id": "jira_2",
                "text": "PROJ-124: Feature - Add dark mode support",
                "timestamp": datetime.now().isoformat(),
                "actor": "David",
                "source": "jira",
                "metadata": {"status": "To Do", "priority": "Medium"}
            }
        ]
    
    try:
        # In production, use proper Jira credentials
        jira_server = os.getenv("JIRA_SERVER", "https://your-domain.atlassian.net")
        jira = JIRA(server=jira_server, token_auth=api_key)
        
        issues = jira.search_issues(f'project={project}', maxResults=50)
        events = []
        
        for issue in issues:
            events.append({
                "id": f"jira_{issue.key}",
                "text": f"{issue.key}: {issue.fields.summary}",
                "timestamp": issue.fields.created,
                "actor": issue.fields.reporter.displayName if issue.fields.reporter else "unknown",
                "source": "jira",
                "metadata": {
                    "status": issue.fields.status.name,
                    "priority": issue.fields.priority.name if issue.fields.priority else "None"
                }
            })
        
        return events
    except Exception as e:
        print(f"Jira API Error: {e}")
        return []


def fetch_gmail_threads(credentials_json: str, label: str) -> List[Dict[str, Any]]:
    """Fetch email threads from Gmail"""
    if not credentials_json:
        # Return mock data for MVP
        return [
            {
                "id": "gmail_1",
                "text": "Email from client: Request for new feature in dashboard",
                "timestamp": datetime.now().isoformat(),
                "actor": "client@example.com",
                "source": "gmail",
                "metadata": {"subject": "Feature Request", "label": label}
            },
            {
                "id": "gmail_2",
                "text": "Email from support: Customer reported issue with payment processing",
                "timestamp": datetime.now().isoformat(),
                "actor": "support@example.com",
                "source": "gmail",
                "metadata": {"subject": "Payment Issue", "label": label}
            }
        ]
    
    try:
        # In production, use proper OAuth2 credentials
        creds = Credentials.from_authorized_user_info(eval(credentials_json))
        service = build('gmail', 'v1', credentials=creds)
        
        results = service.users().messages().list(
            userId='me', labelIds=[label], maxResults=50
        ).execute()
        
        messages = results.get('messages', [])
        events = []
        
        for msg in messages:
            message = service.users().messages().get(userId='me', id=msg['id']).execute()
            headers = message['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
            
            events.append({
                "id": f"gmail_{msg['id']}",
                "text": f"Email: {subject}",
                "timestamp": message['internalDate'],
                "actor": sender,
                "source": "gmail",
                "metadata": {"subject": subject, "label": label}
            })
        
        return events
    except Exception as e:
        print(f"Gmail API Error: {e}")
        return []


def import_csv_buffer(content: bytes, team_id: str) -> List[Dict[str, Any]]:
    """Import events from CSV content buffer"""
    try:
        import io
        df = pd.read_csv(io.BytesIO(content))
        events = []
        
        for idx, row in df.iterrows():
            events.append({
                "id": f"csv_{idx}",
                "text": row.get("text", row.get("description", "")),
                "timestamp": row.get("timestamp", datetime.now().isoformat()),
                "actor": row.get("actor", row.get("user", "unknown")),
                "source": "csv",
                "team_id": team_id,
                "metadata": {k: str(v) for k, v in row.to_dict().items()} # Convert all metadata to strings
            })
        
        return events
    except Exception as e:
        print(f"CSV Buffer Import Error: {e}")
        return []

def import_csv_events(file_path: str, team_id: str) -> List[Dict[str, Any]]:
    """Import events from CSV file (Legacy)"""
    try:
        df = pd.read_csv(file_path)
        events = []
        
        for idx, row in df.iterrows():
            events.append({
                "id": f"csv_{idx}",
                "text": row.get("text", row.get("description", "")),
                "timestamp": row.get("timestamp", datetime.now().isoformat()),
                "actor": row.get("actor", row.get("user", "unknown")),
                "source": "csv",
                "team_id": team_id,
                "metadata": row.to_dict()
            })
        
        return events
    except Exception as e:
        print(f"CSV Import Error: {e}")
        return []
