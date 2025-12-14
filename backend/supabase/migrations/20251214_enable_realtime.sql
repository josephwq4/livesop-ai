-- Enable Realtime for raw_signals
-- This allows the Frontend to subscribe to INSERTs

begin;
  -- Remove if already exists to avoid error (optional, but safe)
  -- alter publication supabase_realtime drop table public.raw_signals;
  
  -- Add table to publication
  alter publication supabase_realtime add table public.raw_signals;
commit;
