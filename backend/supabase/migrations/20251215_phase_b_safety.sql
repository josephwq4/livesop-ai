-- Phase B: Safety & Trust Controls
-- Add global Auto-Pilot kill switch and per-node execution flags

-- 1. Add global Auto-Pilot flag to teams table
ALTER TABLE teams 
ADD COLUMN IF NOT EXISTS auto_pilot_enabled BOOLEAN DEFAULT true;

COMMENT ON COLUMN teams.auto_pilot_enabled IS 'Global kill switch for Auto-Pilot execution. If false, no automations run regardless of node settings.';

-- 2. Add per-node execution flag to workflow_nodes
ALTER TABLE workflow_nodes
ADD COLUMN IF NOT EXISTS auto_run_enabled BOOLEAN DEFAULT false;

COMMENT ON COLUMN workflow_nodes.auto_run_enabled IS 'Per-node Auto-Pilot flag. Node must have this enabled AND global flag enabled to auto-execute.';

-- 3. Create index for performance on auto_pilot queries
CREATE INDEX IF NOT EXISTS idx_teams_auto_pilot ON teams(auto_pilot_enabled);
CREATE INDEX IF NOT EXISTS idx_workflow_nodes_auto_run ON workflow_nodes(auto_run_enabled);

-- Note: No RLS changes needed - existing policies cover these columns
