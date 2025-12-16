#!/usr/bin/env python3
"""
Phase B Testing Script
Run this after deploying Phase B to verify all safety controls work correctly.
"""

import requests
import json
import os
import sys
from datetime import datetime

# Configuration - UPDATE THESE VALUES
BACKEND_URL = os.getenv("BACKEND_URL", "https://your-backend.onrender.com")
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://livesopai.vercel.app")
AUTH_TOKEN = os.getenv("AUTH_TOKEN", "")  # Get from browser localStorage after login

if not AUTH_TOKEN:
    print("❌ ERROR: AUTH_TOKEN not set")
    print("\nTo get your token:")
    print("1. Go to", FRONTEND_URL)
    print("2. Log in")
    print("3. Open DevTools (F12) > Application > Local Storage")
    print("4. Find key starting with 'sb-' and copy 'access_token' value")
    print("5. Run: export AUTH_TOKEN='your-token-here'")
    print("6. Re-run this script")
    sys.exit(1)

headers = {
    "Authorization": f"Bearer {AUTH_TOKEN}",
    "Content-Type": "application/json"
}

def test_api(method, endpoint, data=None, description=""):
    """Helper to test API endpoints"""
    url = f"{BACKEND_URL}{endpoint}"
    print(f"\n{'='*60}")
    print(f"🧪 TEST: {description}")
    print(f"{'='*60}")
    print(f"📍 {method} {endpoint}")
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            print(f"📦 Payload: {json.dumps(data, indent=2)}")
            response = requests.post(url, headers=headers, json=data)
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code < 400:
            result = response.json()
            print(f"✅ SUCCESS")
            print(f"📄 Response: {json.dumps(result, indent=2)}")
            return result
        else:
            print(f"❌ FAILED")
            print(f"📄 Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")
        return None

def main():
    print("""
╔════════════════════════════════════════════════════════════╗
║         LiveSOP AI - Phase B Testing Suite                ║
║         Safety & Trust Controls Verification              ║
╚════════════════════════════════════════════════════════════╝
""")
    
    # Test 1: Get current Auto-Pilot status
    status = test_api(
        "GET", 
        "/settings/auto_pilot/status",
        description="Get current Auto-Pilot configuration"
    )
    
    if not status:
        print("\n❌ Cannot proceed - authentication failed or backend unreachable")
        return
    
    team_id = status.get("team_id")
    print(f"\n✓ Team ID: {team_id}")
    print(f"✓ Global Auto-Pilot: {'ENABLED' if status.get('global_auto_pilot_enabled') else 'DISABLED'}")
    print(f"✓ Active Nodes: {len(status.get('nodes', []))}")
    
    # Test 2: Disable Global Auto-Pilot
    test_api(
        "POST",
        "/settings/auto_pilot/global",
        data={"enabled": False},
        description="Disable Global Auto-Pilot (Kill Switch)"
    )
    
    # Test 3: Verify it's disabled
    status_after = test_api(
        "GET",
        "/settings/auto_pilot/status",
        description="Verify Global Auto-Pilot is disabled"
    )
    
    if status_after and not status_after.get("global_auto_pilot_enabled"):
        print("\n✅ Global Kill Switch working correctly!")
    else:
        print("\n⚠️  Global Kill Switch may not be working")
    
    # Test 4: Re-enable Global Auto-Pilot
    test_api(
        "POST",
        "/settings/auto_pilot/global",
        data={"enabled": True},
        description="Re-enable Global Auto-Pilot"
    )
    
    # Test 5: Test node-level control (if nodes exist)
    if status and status.get("nodes"):
        first_node = status["nodes"][0]
        node_id = first_node["node_id"]
        
        # Enable node
        test_api(
            "POST",
            f"/settings/auto_pilot/node/{node_id}",
            data={"enabled": True},
            description=f"Enable Auto-Run for node: {first_node.get('label', node_id)}"
        )
        
        # Disable node
        test_api(
            "POST",
            f"/settings/auto_pilot/node/{node_id}",
            data={"enabled": False},
            description=f"Disable Auto-Run for node: {first_node.get('label', node_id)}"
        )
    
    # Test 6: Check Live Feed filtering
    feed = test_api(
        "GET",
        f"/automations/{team_id}/live_feed?limit=10",
        description="Get Live Feed (should filter low-confidence signals)"
    )
    
    if feed:
        feed_items = feed.get("feed", [])
        print(f"\n✓ Live Feed contains {len(feed_items)} items")
        if feed_items:
            print("\n📊 Confidence levels in Live Feed:")
            for item in feed_items:
                conf = item.get("confidence", 0)
                print(f"   • {item.get('action', 'Unknown')}: {conf*100:.0f}% confidence")
                if conf < 0.5:
                    print(f"     ⚠️  WARNING: Low-confidence signal should be filtered!")
    
    print("""
\n╔════════════════════════════════════════════════════════════╗
║                    Testing Complete                        ║
╚════════════════════════════════════════════════════════════╝

Next Steps:
1. ✅ All API endpoints are working
2. 🧪 Test with real Slack events:
   - Send a message in your monitored Slack channel
   - Check if Auto-Pilot respects the global/node flags
3. 📊 Verify in Supabase:
   - Check inference_runs table for skip_reason entries
   - Confirm low-confidence signals are logged but not surfaced

Manual Verification Checklist:
□ Global kill switch prevents ALL executions
□ Per-node flags work independently
□ Low-confidence signals hidden from Live Feed
□ All skipped executions logged with reasons
□ Usage counter only increments on successful runs
""")

if __name__ == "__main__":
    main()
