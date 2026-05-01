
CREATE_TABLES_SQL = '''
CREATE TABLE IF NOT EXISTS conversations (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query           TEXT NOT NULL,
    rewritten_query TEXT,
    answer          TEXT NOT NULL,
    hallucination_risk FLOAT NOT NULL,
    flagged         BOOLEAN NOT NULL,
