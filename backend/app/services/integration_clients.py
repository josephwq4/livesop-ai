import os
from typing import List, Dict, Any

from datetime import datetime



def fetch_all_events(team_id: str) -> List[Dict[str, Any]]:
    """Combine events from all integrated sources"""
    all_events = []
    
    # Fetch from different sources
    # In production, these would use team-specific credentials from database
    # Fetch from different sources
    # In production, these would use team-specific credentials from database
    try:
        # Get channels from env or default to commonly used ones
        channels_env = os.getenv("SLACK_CHANNELS", "new-channel,general,random")
        channels = [c.strip() for c in channels_env.split(",")]
        
        slack_events = fetch_slack_events(os.getenv("SLACK_TOKEN", ""), channels)
        all_events.extend(slack_events)
    except Exception as e:
        print(f"Error fetching Slack events: {e}")
    
    try:
        # Align env var names (API_TOKEN is usually what we set)
        jira_token = os.getenv("JIRA_API_TOKEN") or os.getenv("JIRA_API_KEY", "")
        jira_project = os.getenv("JIRA_PROJECT", "PROJ")
        
        jira_events = fetch_jira_issues(jira_token, jira_project)
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


# In-memory user cache with timestamp (Simple implementation)
_slack_user_cache: Dict[str, str] = {}
_cache_timestamp: float = 0
CACHE_TTL = 3600  # 1 hour

def _get_slack_users_map(client: Any) -> Dict[str, str]:
    """Fetch all users and map ID -> Real Name. Uses caching."""
    global _slack_user_cache, _cache_timestamp
    import time
    
    current_time = time.time()
    if _slack_user_cache and (current_time - _cache_timestamp < CACHE_TTL):
        return _slack_user_cache

    try:
        # Fetch all users (pagination might be needed for huge teams, keeping simple for now)
        response = client.users_list(limit=200)
        user_map = {}
        for user in response["members"]:
            profile = user.get("profile", {})
            # Use display name, fallback to real name, fallback to name
            name = profile.get("display_name") or profile.get("real_name") or user.get("name")
            user_map[user["id"]] = name
        
        _slack_user_cache = user_map
        _cache_timestamp = current_time
        print(f"Refreshed Slack User Cache: {len(user_map)} users")
        return user_map
    except SlackApiError as e:
        print(f"Warning: Could not resolve Slack users: {e}")
        return {}

def _classify_signal(text: str) -> str:
    """Heuristic classification of message intent"""
    text_lower = text.lower()
    
    # Keywords for heuristic classification
    if any(w in text_lower for w in ["over to", "taking look", "assigned", "handing off"]):
        return "handoff"
    if any(w in text_lower for w in ["approved", "lgtm", "merged", "signed off", "looks good"]):
        return "approval"
    if any(w in text_lower for w in ["blocked", "stuck", "hold", "fail", "error", "breaking"]):
        return "blocker"
    if any(w in text_lower for w in ["status", "update", "progress", "completed", "done", "fixed"]):
        return "status_update"
        
    return "unknown"

def fetch_slack_events(token: str, channels: List[str]) -> List[Dict[str, Any]]:
    """Fetch structured workflow signals from Slack channels"""
    if not token:
        # Return mock data for MVP
        return [
            {
                "id": "slack_1",
                "text": "Alice: Started working on the new feature deployment",
                "timestamp": datetime.now().isoformat(),
                "actor": "Alice",
                "source": "slack",
                "signal_type": "status_update",
                "thread_role": "root",
                "metadata": {"channel": "general"}
            }
        ]
    
    try:
        from slack_sdk import WebClient
        client = WebClient(token=token)
        events = []
        user_map = _get_slack_users_map(client)
        
        # Helper to resolve channel ID
        def _resolve_channel_id(name_or_id):
            if name_or_id.startswith("C"): return name_or_id
            try:
                # Cache this in production!
                for result in client.conversations_list():
                    for channel in result["channels"]:
                        if channel["name"] == name_or_id:
                            return channel["id"]
            except Exception:
                pass
            return name_or_id

        for channel_name in channels:
            channel_id = _resolve_channel_id(channel_name)
            
            # 1. Fetch History (Roots)
            try:
                history = client.conversations_history(channel=channel_id, limit=20)
            except Exception as e:
                print(f"Error reading channel {channel_name} ({channel_id}): {e}")
                continue

            for msg in history["messages"]:
                if msg.get("type") != "message" or msg.get("subtype"):
                    continue

                text = msg.get("text", "")
                user_id = msg.get("user", "")
                ts = msg.get("ts")
                
                # Resolve Actor
                actor = user_map.get(user_id, f"User_{user_id}")
                
                # Filter noise: Short messages that are NOT threads
                if len(text) < 5 and "thread_ts" not in msg:
                    continue

                # Process Root Message
                root_event = {
                    "id": f"slack_{ts}",
                    "text": text,
                    "timestamp": datetime.fromtimestamp(float(ts)).isoformat(),
                    "actor": actor,
                    "source": "slack",
                    "signal_type": _classify_signal(text),
                    "thread_role": "thread_root",
                    "metadata": {"channel": channel, "thread_ts": ts}
                }
                print(f"🔍 [SIGNAL] {root_event['signal_type'].upper()}: {text[:50]}... ({actor})")
                events.append(root_event)
                
                # 2. Fetch Replies (if thread exists)
                if msg.get("reply_count", 0) > 0:
                    try:
                        replies_resp = client.conversations_replies(channel=channel, ts=ts, limit=10)
                        for reply in replies_resp["messages"]:
                            if reply["ts"] == ts: continue # Skip root (already added)
                            
                            r_text = reply.get("text", "")
                            r_user = reply.get("user", "")
                            r_actor = user_map.get(r_user, f"User_{r_user}")
                            
                            # Replies are valuable even if short (e.g. "Approved")
                            
                            events.append({
                                "id": f"slack_{reply['ts']}",
                                "text": r_text,
                                "timestamp": datetime.fromtimestamp(float(reply['ts'])).isoformat(),
                                "actor": r_actor,
                                "source": "slack",
                                "signal_type": _classify_signal(r_text),
                                "thread_role": "thread_reply",
                                "metadata": {"channel": channel, "root_ts": ts}
                            })
                    except Exception as e:
                        print(f"Error fetching replies for {ts}: {e}")

        return events
    except Exception as e:
        print(f"Slack Client Error: {e}")
        return []



def fetch_slack_history_for_kb(token: str, channels: List[str], limit_per_channel: int = 50) -> List[Dict]:
    """Fetch history items for Knowledge Base"""
    if not token: return []
    try:
        from slack_sdk import WebClient
        client = WebClient(token=token)
        items = []
        user_map = _get_slack_users_map(client)

        for channel_name in channels:
            channel_id = channel_name
            # Resolve Name -> ID
            if not channel_name.startswith("C"):
                try:
                    for result in client.conversations_list(types="public_channel,private_channel"):
                        for c in result["channels"]:
                            if c["name"] == channel_name:
                                channel_id = c["id"]
                                break
                except: pass

            try:
                history = client.conversations_history(channel=channel_id, limit=limit_per_channel)
                if not history.get("messages"): continue
                
                for msg in history["messages"]:
                    text = msg.get("text", "")
                    if not text or len(text) < 15: continue # Skip short/empty
                    if msg.get("subtype"): continue 
                    
                    user = msg.get("user")
                    actor = user_map.get(user, user)
                    ts = float(msg.get("ts", 0))
                    
                    items.append({
                        "content": f"Slack #{channel_name} ({actor}): {text}",
                        "metadata": {
                            "source": "slack",
                            "subtype": "history",
                            "channel": channel_name,
                            "actor": actor,
                            "timestamp": datetime.fromtimestamp(ts).isoformat(),
                            "slack_ts": msg["ts"],
                            "filename": f"Slack #{channel_name} Log"
                        }
                    })
            except Exception as e:
                print(f"Error fetching logs for {channel_name}: {e}")
                
        return items
    except Exception as e:
        print(f"Slack History Fetch Error: {e}")
        return []

def fetch_jira_issues(api_key: str, project: str) -> List[Dict[str, Any]]:
    """Fetch issues from Jira project"""
    
    # Fallback to env vars if inputs are placeholders
    jira_server = os.getenv("JIRA_SERVER", "https://your-domain.atlassian.net")
    jira_email = os.getenv("JIRA_EMAIL", "")
    
    # If using UI input "env", load from backend env
    if api_key == "env":
        api_key = os.getenv("JIRA_API_TOKEN", "")
    
    if not api_key or not project:
         # Return mock data for MVP if no creds
        if not os.getenv("JIRA_API_TOKEN"):
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
        from jira import JIRA
        # Jira Cloud requires Email + API Token (Basic Auth)
        # Verify if we have an email, otherwise try token_auth (PAT)
        if jira_email and "@" in jira_email:
             # Basic Auth (Cloud standard)
             jira_options = {'server': jira_server}
             jira = JIRA(options=jira_options, basic_auth=(jira_email, api_key))
        else:
             # PAT or Server/DC
             jira = JIRA(server=jira_server, token_auth=api_key)
        
        print(f"Connecting to Jira: {jira_server} for project {project}")
        issues = jira.search_issues(f'project={project} ORDER BY created DESC', maxResults=50)
        events = []
        
        for issue in issues:
            # Extract status safely
            status = issue.fields.status.name if hasattr(issue.fields, "status") else "Unknown"
            priority = issue.fields.priority.name if hasattr(issue.fields, "priority") and issue.fields.priority else "None"
            
            events.append({
                "id": f"jira_{issue.key}",
                "text": f"{issue.key}: {issue.fields.summary} ({status})",
                "timestamp": issue.fields.created,
                "actor": issue.fields.reporter.displayName if hasattr(issue.fields, "reporter") and issue.fields.reporter else "unknown",
                "source": "jira",
                "signal_type": "status_update", # Default signal for Jira
                "metadata": {
                    "status": status,
                    "priority": priority,
                    "url": f"{jira_server}/browse/{issue.key}"
                }
            })
        
        return events
    except Exception as e:
        print(f"Jira API Error: {e}")
        # import traceback
        # traceback.print_exc()
        # Return empty list instead of crashing, but print error
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
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        
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


import csv
import io

def import_csv_buffer(content: bytes, team_id: str) -> List[Dict[str, Any]]:
    """Import events from CSV content buffer using (No Pandas)"""
    try:
        # Decode bytes to string wrapper
        text_stream = io.TextIOWrapper(io.BytesIO(content), encoding='utf-8')
        reader = csv.DictReader(text_stream)
        
        events = []
        for idx, row in enumerate(reader):
            events.append({
                "id": f"csv_{idx}",
                "text": row.get("text") or row.get("description", ""),
                "timestamp": row.get("timestamp", datetime.now().isoformat()),
                "actor": row.get("actor") or row.get("user", "unknown"),
                "source": "csv",
                "team_id": team_id,
                "metadata": dict(row)
            })
        
        return events
    except Exception as e:
        print(f"CSV Buffer Import Error: {e}")
        return []

def import_csv_events(file_path: str, team_id: str) -> List[Dict[str, Any]]:
    """Import events from CSV file (No Pandas)"""
    try:
        events = []
        with open(file_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for idx, row in enumerate(reader):
                events.append({
                    "id": f"csv_{idx}",
                    "text": row.get("text") or row.get("description", ""),
                    "timestamp": row.get("timestamp", datetime.now().isoformat()),
                    "actor": row.get("actor") or row.get("user", "unknown"),
                    "source": "csv",
                    "team_id": team_id,
                    "metadata": dict(row)
                })
        
        return events
    except Exception as e:
        print(f"CSV Import Error: {e}")
        return []

# --- WRITING (AUTOMATION) ---

def send_slack_message(token: str, channel: str, text: str) -> Dict[str, Any]:
    """Send a message to a Slack channel"""
    if not token or not channel:
        return {"success": False, "error": "Missing token or channel"}
        
    try:
        from slack_sdk import WebClient
        
        client = WebClient(token=token)
        # Handle channel name vs ID if needed, but chat_postMessage handles usage of name usually?
        # Ideally using an ID is safer.
        response = client.chat_postMessage(channel=channel, text=text)
        return {"success": True, "ts": response["ts"]}
    except Exception as e:
        # If it was a SlackApiError, it has a response attribute. Exception might not.
        error_msg = str(e)
        if hasattr(e, 'response') and 'error' in e.response:
             error_msg = str(e.response['error'])
        
        print(f"Slack Send Error: {error_msg}")
        return {"success": False, "error": error_msg}

def create_jira_issue(api_key: str, project_key: str, summary: str, description: str, issue_type: str = "Task") -> Dict[str, Any]:
    """Create a Jira ticket"""
    jira_server = os.getenv("JIRA_URL") or os.getenv("JIRA_SERVER", "https://your-domain.atlassian.net")
    jira_email = os.getenv("JIRA_EMAIL", "")

    # Resolve token/auth
    if api_key == "env": 
        api_key = os.getenv("JIRA_API_KEY") or os.getenv("JIRA_API_TOKEN", "")
    
    if not api_key:
         return {"success": False, "error": "Missing Jira API Token"}
    if not project_key:
         return {"success": False, "error": "Missing Project Key"}

    try:
        from jira import JIRA
        if jira_email and "@" in jira_email:
             jira = JIRA(server=jira_server, basic_auth=(jira_email, api_key))
        else:
             jira = JIRA(server=jira_server, token_auth=api_key)
        
        issue_dict = {
            'project': {'key': project_key},
            'summary': summary,
            'description': description,
            'issuetype': {'name': issue_type},
        }
        new_issue = jira.create_issue(fields=issue_dict)
        return {
            "success": True, 
            "key": new_issue.key, 
            "url": f"{jira_server}/browse/{new_issue.key}"
        }
    except Exception as e:
        print(f"Jira Create Error: {e}")
        return {"success": False, "error": str(e)}

def fetch_notion_docs_for_kb(api_key: str) -> List[Dict]:
    """Fetch Notion documents using requests (Sync) - Replaces httpx for stability"""
    import requests
    if not api_key: return []
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    
    try:
        with requests.Session() as client:
            # 1. Search for all pages
            search_res = client.post("https://api.notion.com/v1/search", 
                headers=headers, 
                json={"filter": {"value": "page", "property": "object"}}
            )
            if search_res.status_code != 200:
                print(f"Notion Search Failed: {search_res.text}")
                return []

            data = search_res.json()
            results = data.get("results", [])
            
            items = []
            for page in results:
                page_id = page["id"]
                
                # Title extraction
                title = "Untitled"
                props = page.get("properties", {})
                for key, val in props.items():
                    if val["type"] == "title" and val["title"]:
                        title = val["title"][0]["plain_text"]
                        break
                        
                # 2. Fetch Blocks (Content)
                try:
                    blocks_res = client.get(f"https://api.notion.com/v1/blocks/{page_id}/children?page_size=100", headers=headers)
                    if blocks_res.status_code != 200: continue
                    
                    blocks_data = blocks_res.json()
                    content_lines = []
                    
                    for block in blocks_data.get("results", []):
                        btype = block["type"]
                        # Extract basic text
                        if btype in block and isinstance(block[btype], dict) and "rich_text" in block[btype]:
                             text_objs = block[btype]["rich_text"]
                             text = "".join([t["plain_text"] for t in text_objs])
                             if text: content_lines.append(text)
                    
                    full_text = "\n".join(content_lines)
                    if not full_text or len(full_text) < 20: continue
                    
                    items.append({
                        "content": f"Notion Page: {title}\n\n{full_text}",
                        "metadata": {
                            "source": "notion",
                            "subtype": "page",
                            "page_id": page_id,
                            "title": title,
                            "url": page.get("url"),
                            "filename": f"Notion: {title}"
                        }
                    })
                except Exception as be:
                    print(f"Error fetching blocks for {page_id}: {be}")
            
            return items

    except Exception as e:
        print(f"Notion Fetch Error: {e}")
        return []
