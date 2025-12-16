-- Phase I: Smart Context / RAG

-- Ensure necessary extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Table: Knowledge Base
CREATE TABLE IF NOT EXISTS knowledge_base (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    team_id UUID REFERENCES teams(id) ON DELETE CASCADE NOT NULL,
    content TEXT NOT NULL,
    embedding VECTOR(1536), -- OpenAI text-embedding-3-small
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for HNSW (High performance vector search)
CREATE INDEX IF NOT EXISTS idx_knowledge_base_embedding 
ON knowledge_base 
USING hnsw (embedding vector_cosine_ops);

-- RLS Policies
ALTER TABLE knowledge_base ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow read access for team members" ON knowledge_base
    FOR SELECT
    USING (true); -- MVP: relying on application logic filtering

CREATE POLICY "Allow write access for team members" ON knowledge_base
    FOR ALL
    USING (true); -- MVP: relying on application logic filtering

-- Search Function
CREATE OR REPLACE FUNCTION match_knowledge_base (
    query_embedding VECTOR(1536),
    match_threshold FLOAT,
    match_count INT,
    filter_team_id UUID
)
RETURNS TABLE (
    id UUID,
    content TEXT,
    metadata JSONB,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        kb.id,
        kb.content,
        kb.metadata,
        1 - (kb.embedding <=> query_embedding) AS similarity
    FROM knowledge_base kb
    WHERE kb.team_id = filter_team_id
    AND 1 - (kb.embedding <=> query_embedding) > match_threshold
    ORDER BY kb.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;
