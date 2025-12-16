# Phase B Testing Guide
# Execute these steps in order to verify all safety controls

## STEP 1: Apply Database Migration
# Option A: Via Supabase Dashboard (Recommended)
1. Go to https://supabase.com/dashboard
2. Select your LiveSOP project
3. Click "SQL Editor" in the left sidebar
4. Click "New Query"
5. Copy the contents of `backend/supabase/migrations/20251215_phase_b_safety.sql`
6. Paste into the SQL editor
7. Click "Run" (or press Ctrl+Enter)
8. Verify you see "Success. No rows returned"

# Option B: Via Supabase CLI (if installed)
# From project root:
supabase db push

## STEP 2: Verify Migration Applied
# Run this query in Supabase SQL Editor to confirm:
SELECT column_name, data_type, column_default 
FROM information_schema.columns 
WHERE table_name = 'teams' AND column_name = 'auto_pilot_enabled';

# Should return:
# column_name: auto_pilot_enabled
# data_type: boolean
# column_default: true

## STEP 3: Get Your Authentication Token
# You need a valid JWT token to call the API endpoints
# Option A: From Browser DevTools
1. Open your deployed frontend (https://livesopai.vercel.app)
2. Log in
3. Open DevTools (F12)
4. Go to Application > Local Storage
5. Find key starting with "sb-" 
6. Copy the "access_token" value

# Option B: From Supabase Dashboard
1. Go to Authentication > Users
2. Click on your user
3. Copy the "User UID" 
4. Use Supabase's "Generate Access Token" feature

## STEP 4: Test Global Kill Switch

# A. Get current status
curl -X GET "https://your-backend.onrender.com/settings/auto_pilot/status" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json"

# Expected response:
{
  "success": true,
  "team_id": "uuid-here",
  "global_auto_pilot_enabled": true,
  "nodes": [...]
}

# B. Disable Auto-Pilot globally
curl -X POST "https://your-backend.onrender.com/settings/auto_pilot/global" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"enabled": false}'

# Expected response:
{
  "success": true,
  "team_id": "uuid-here",
  "auto_pilot_enabled": false,
  "message": "Global Auto-Pilot disabled"
}

# C. Trigger a Slack event (if webhook configured)
# Send a message in your monitored Slack channel that would normally trigger automation
# Example: "Critical bug in production - need Jira ticket"

# D. Verify no automation executed
# Check Live Feed in dashboard - should see evaluation logged but status = "skipped"
# Or query directly:
SELECT id, trigger_type, status, model_config->>'skip_reason' as skip_reason
FROM inference_runs 
WHERE team_id = 'YOUR_TEAM_ID'
ORDER BY started_at DESC 
LIMIT 5;

# Should show: skip_reason = "global_auto_pilot_disabled"

# E. Re-enable Auto-Pilot
curl -X POST "https://your-backend.onrender.com/settings/auto_pilot/global" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"enabled": true}'

## STEP 5: Test Per-Node Control

# A. Get your workflow and node IDs
curl -X GET "https://your-backend.onrender.com/workflows/team123/workflows" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# From response, copy a node's "id" (e.g., "step_2")

# B. Enable Auto-Run for specific node
curl -X POST "https://your-backend.onrender.com/settings/auto_pilot/node/step_2" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"enabled": true}'

# Expected response:
{
  "success": true,
  "node_id": "step_2",
  "auto_run_enabled": true,
  "message": "Auto-Run enabled for node step_2"
}

# C. Send Slack message that matches this node
# The system should now execute ONLY this node

# D. Disable the node
curl -X POST "https://your-backend.onrender.com/settings/auto_pilot/node/step_2" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"enabled": false}'

## STEP 6: Test Low-Confidence Filtering

# A. Check current Live Feed
curl -X GET "https://your-backend.onrender.com/automations/YOUR_TEAM_ID/live_feed?limit=20" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# Note: Only signals with confidence >= 0.5 should appear

# B. Query database directly to see ALL signals (including low-confidence)
SELECT 
  id,
  trigger_type,
  status,
  model_config->>'confidence' as confidence,
  model_config->>'matched_node' as node,
  started_at
FROM inference_runs 
WHERE team_id = 'YOUR_TEAM_ID'
ORDER BY started_at DESC 
LIMIT 20;

# You should see entries with confidence < 0.5 that DON'T appear in Live Feed

## STEP 7: End-to-End Smoke Test

# 1. Enable global Auto-Pilot
# 2. Enable Auto-Run for one specific node (e.g., "Create Jira Ticket")
# 3. Send Slack message: "Bug found - create ticket"
# 4. Verify:
#    - Jira ticket created automatically
#    - Live Feed shows the execution
#    - inference_runs has full audit trail
#    - Usage counter incremented

## TROUBLESHOOTING

# If API returns 401 Unauthorized:
# - Your token expired, get a new one from step 3

# If migration fails:
# - Check if columns already exist (re-running is safe)
# - Verify you have admin access to Supabase project

# If Auto-Pilot doesn't execute:
# - Check global flag: GET /settings/auto_pilot/status
# - Check node flag: Ensure auto_run_enabled = true
# - Check confidence: Must be >= 0.9 for execution
# - Check logs in Render dashboard for errors

# If Live Feed is empty:
# - Check if confidence threshold is too high
# - Query inference_runs directly to see raw data
# - Verify team_id matches between requests
