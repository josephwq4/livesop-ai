-- Enable vector extension (should be on, but ensure)
create extension if not exists vector;

-- Create similarity search function for RAG
-- Usage: select * from match_signals('[...]', 0.7, 5, 'team_uuid')
create or replace function match_signals (
  query_embedding vector(1536),
  match_threshold float,
  match_count int,
  filter_team_id uuid
)
returns table (
  id uuid,
  content text,
  occurred_at timestamptz,
  similarity float
)
language plpgsql
as $$
begin
  return query
  select
    raw_signals.id,
    raw_signals.content,
    raw_signals.occurred_at,
    1 - (raw_signals.embedding <=> query_embedding) as similarity
  from raw_signals
  where 1 - (raw_signals.embedding <=> query_embedding) > match_threshold
  and raw_signals.team_id = filter_team_id
  order by raw_signals.embedding <=> query_embedding
  limit match_count;
end;
$$;
