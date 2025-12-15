import os
import sys
from pathlib import Path

# Add backend directory to python path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

# Helper to load env vars from backend/.env
def load_env():
    env_path = backend_dir / '.env'
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, val = line.strip().split('=', 1)
                    os.environ[key] = val

load_env()

from supabase import create_client, Client

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_KEY")

if not url or not key:
    print("Error: Missing credentials")
    sys.exit(1)

supabase: Client = create_client(url, key)

# Demo data for "team123" (Hardcoded in Dashboard.jsx Phase A)
data = [
    {
        "team_id": "team123",
        "source": "slack",
        "author": "Alice ( CSM)",
        "content": "Urgent: Enterprise customer Globex is reporting 502 errors on the dashboard login page. It started 10 mins ago.",
        "timestamp": "2025-12-15T09:00:00Z"
    },
    {
        "team_id": "team123",
        "source": "slack",
        "author": "Bob (DevOps)",
        "content": "Checking the load balancer... looks like a spike in traffic. But also seeing DB connection timeouts.",
        "timestamp": "2025-12-15T09:05:00Z"
    },
    {
        "team_id": "team123",
        "source": "jira",
        "author": "System",
        "content": "Ticket CORP-101 Created: Investigate Login Latency. Priority: High.",
        "timestamp": "2025-12-15T09:06:00Z"
    },
    {
        "team_id": "team123",
        "source": "slack",
        "author": "Alice (CSM)",
        "content": "Thanks Bob. I'll notify the customer status page is updated.",
        "timestamp": "2025-12-15T09:10:00Z"
    }
]

print("Seeding demo data...")
for row in data:
    try:
        # Check duplicates to avoid flooding if run multiple times
        # Ideally we'd just insert, Supabase handles it.
        supabase.table("raw_signals").insert(row).execute()
    except Exception as e:
        print(f"Skipping row (maybe exists): {e}")

print("Seeding complete.")
