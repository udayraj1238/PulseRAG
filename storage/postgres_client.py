
CREATE_TABLES_SQL = '''
CREATE TABLE IF NOT EXISTS conversations (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query           TEXT NOT NULL,
    rewritten_query TEXT,
    answer          TEXT NOT NULL,
    hallucination_risk FLOAT NOT NULL,
    flagged         BOOLEAN NOT NULL,
    retrieval_attempts INTEGER NOT NULL,
    cache_hit       BOOLEAN NOT NULL,
    total_latency_ms FLOAT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS feedback (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id),
    rating          SMALLINT CHECK (rating IN (-1, 1)),  -- -1 = thumbs down, 1 = thumbs up
    comment         TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

