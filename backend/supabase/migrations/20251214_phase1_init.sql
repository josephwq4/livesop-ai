-- Enable pgvector extension (for future embeddings)
create extension if not exists vector;

-- 1. TEAMS TABLE (The Root Tenant)
create table public.teams (
  id uuid default gen_random_uuid() primary key,
  name text not null,
  owner_id uuid references auth.users(id) on delete cascade not null, -- Links to Supabase Auth
  created_at timestamptz default now() not null
);
-- Enable RLS
alter table public.teams enable row level security;

-- 2. RAW SIGNALS (The Data Lake)
create table public.raw_signals (
  id uuid default gen_random_uuid() primary key,
  team_id uuid references public.teams(id) on delete cascade not null,
  source text not null, -- 'slack', 'jira', 'manual'
  external_id text not null, -- Slack 'ts' or Jira 'issue_id'
  actor text, -- 'username' or 'email'
  content text not null, -- The raw message body
  metadata jsonb default '{}'::jsonb, -- Store channel_id, thread_ts, priority here
  embedding vector(1536), -- Nullable for Phase 1
  occurred_at timestamptz not null, -- Source timestamp
  created_at timestamptz default now() not null,
  
  -- Prevent duplicate ingestion of same message
  unique (team_id, source, external_id)
);
-- Enable RLS
alter table public.raw_signals enable row level security;

-- Index for "Get recent context"
create index idx_raw_signals_team_occurred on public.raw_signals(team_id, occurred_at desc);
-- Index for vector search (prepared for Phase 2)
create index idx_raw_signals_embedding on public.raw_signals using ivfflat (embedding vector_cosine_ops)
  with (lists = 100); 

-- 3. INFERENCE RUNS (The Audit Log)
create table public.inference_runs (
  id uuid default gen_random_uuid() primary key,
  team_id uuid references public.teams(id) on delete cascade not null,
  trigger_type text not null, -- 'manual_dashboard', 'webhook', 'scheduled'
  status text not null default 'pending', -- 'processing', 'completed', 'failed'
  started_at timestamptz default now() not null,
  completed_at timestamptz,
  model_config jsonb default '{}'::jsonb -- Stores prompts/params used
);
-- Enable RLS
alter table public.inference_runs enable row level security;

-- Index for Dashboard History
create index idx_inference_runs_team_started on public.inference_runs(team_id, started_at desc);

-- 4. JOIN TABLE: Signals <-> Inference (Explicit Provenance)
create table public.inference_run_signals (
  inference_run_id uuid references public.inference_runs(id) on delete cascade not null,
  signal_id uuid references public.raw_signals(id) on delete cascade not null,
  primary key (inference_run_id, signal_id)
);
-- Enable RLS
alter table public.inference_run_signals enable row level security;

-- 5. WORKFLOWS (The Generated Artifact)
create table public.workflows (
  id uuid default gen_random_uuid() primary key,
  team_id uuid references public.teams(id) on delete cascade not null,
  inference_run_id uuid references public.inference_runs(id), -- Nullable if created manually
  title text not null default 'Untitled Workflow',
  is_active boolean default false not null,
  created_at timestamptz default now() not null
);
-- Enable RLS
alter table public.workflows enable row level security;

-- PARTIAL UNIQUE INDEX constraint for Active Version enforcement
create unique index idx_unique_active_workflow 
  on public.workflows(team_id) 
  where is_active = true;

-- Index for "Get Current SOP" performance
create index idx_workflows_team_created on public.workflows(team_id, created_at desc);

-- 6. WORKFLOW NODES (Steps)
create table public.workflow_nodes (
  id uuid default gen_random_uuid() primary key,
  workflow_id uuid references public.workflows(id) on delete cascade not null,
  step_id text not null, -- Internal ID 'node_1'
  label text not null,
  description text,
  type text default 'process', -- 'trigger', 'process', 'decision'
  actor text,
  metadata jsonb default '{}'::jsonb
);
-- Enable RLS
alter table public.workflow_nodes enable row level security;

create index idx_nodes_workflow on public.workflow_nodes(workflow_id);

-- 7. WORKFLOW EDGES (Transitions)
create table public.workflow_edges (
  id uuid default gen_random_uuid() primary key,
  workflow_id uuid references public.workflows(id) on delete cascade not null,
  source_step_id text not null,
  target_step_id text not null,
  label text,
  condition text
);
-- Enable RLS
alter table public.workflow_edges enable row level security;

create index idx_edges_workflow on public.workflow_edges(workflow_id);

-- ----------- RLS POLICIES (Basic) -----------

-- Helper to check if user owns the team
create or replace function public.is_team_owner(team_uuid uuid)
returns boolean as $$
begin
  return exists (
    select 1 from public.teams 
    where id = team_uuid and owner_id = auth.uid()
  );
end;
$$ language plpgsql security definer;

-- Teams: Owners can view/edit their own team
create policy "Owners can view their teams" on public.teams
  for select using (auth.uid() = owner_id);

create policy "Owners can update their teams" on public.teams
  for update using (auth.uid() = owner_id);

-- Raw Signals: View if team owner
create policy "Team owners view signals" on public.raw_signals
  for select using (public.is_team_owner(team_id));

create policy "Team owners insert signals" on public.raw_signals
  for insert with check (public.is_team_owner(team_id));

-- (Repeat pattern for other tables - Simplified for Migration file length)
create policy "Team owners view runs" on public.inference_runs
  for select using (public.is_team_owner(team_id));

create policy "Team owners insert runs" on public.inference_runs
  for insert with check (public.is_team_owner(team_id));

create policy "Team owners view workflows" on public.workflows
  for select using (public.is_team_owner(team_id));

create policy "Team owners manage workflows" on public.workflows
  for all using (public.is_team_owner(team_id));

-- Nodes/Edges inherit access via workflow->team check (slightly more complex join, 
-- usually handled by app logic + simple RLS or a wrapper function. 
-- For MVP Migration, we will allow auth users who own the parent team)

create policy "Team owners view nodes" on public.workflow_nodes
  for select using (
    exists (select 1 from public.workflows w 
            where w.id = workflow_nodes.workflow_id 
            and public.is_team_owner(w.team_id))
  );

create policy "Team owners view edges" on public.workflow_edges
  for select using (
    exists (select 1 from public.workflows w 
            where w.id = workflow_edges.workflow_id 
            and public.is_team_owner(w.team_id))
  );
