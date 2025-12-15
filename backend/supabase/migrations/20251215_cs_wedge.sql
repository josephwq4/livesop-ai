-- 1. TEAM USAGE (For Trial Limits)
create table public.team_usage (
  id uuid default gen_random_uuid() primary key,
  team_id uuid references public.teams(id) on delete cascade not null,
  period_start timestamptz default now() not null,
  period_end timestamptz,
  automation_count int default 0 not null,
  automation_limit int default 100 not null, -- Trial default
  plan_tier text default 'free', -- 'free', 'pro', 'enterprise'
  created_at timestamptz default now() not null,
  updated_at timestamptz default now() not null
);

-- Enable RLS
alter table public.team_usage enable row level security;

-- Policies
create policy "Team owners view usage" on public.team_usage
  for select using (public.is_team_owner(team_id));

-- Trigger to update updated_at
create or replace function public.trigger_set_timestamp()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

create trigger set_timestamp
before update on public.team_usage
for each row
execute procedure public.trigger_set_timestamp();


-- 2. CHANNEL CONFIGS (For Escalation Templates)
create table public.channel_configs (
  id uuid default gen_random_uuid() primary key,
  team_id uuid references public.teams(id) on delete cascade not null,
  channel_id text not null, -- Slack channel ID
  channel_name text,
  workflow_template text, -- 'escalation_tier_3', 'bug_report', etc.
  auto_pilot_enabled boolean default false,
  config jsonb default '{}'::jsonb, -- Store specific params like 'jira_project_key'
  created_at timestamptz default now() not null,
  updated_at timestamptz default now() not null,
  
  unique(team_id, channel_id)
);

-- Enable RLS
alter table public.channel_configs enable row level security;

-- Policies
create policy "Team owners view configs" on public.channel_configs
  for select using (public.is_team_owner(team_id));

create policy "Team owners manage configs" on public.channel_configs
  for all using (public.is_team_owner(team_id));

create trigger set_timestamp_configs
before update on public.channel_configs
for each row
execute procedure public.trigger_set_timestamp();
