import os
from supabase import create_client, Client

url: str = os.environ.get("SUPABASE_URL", "")
key: str = os.environ.get("SUPABASE_SERVICE_KEY", "")

# Fallback for localized dev without DB
if not url or "your-project" in url:
    print("⚠️ Supabase URL not properly configured. Persistence will fail.")
    supabase_admin: Client = None # type: ignore
else:
    supabase_admin: Client = create_client(url, key)

def get_supabase_client() -> Client:
    """Returns the admin client (Service Role) for backend operations"""
    return supabase_admin
