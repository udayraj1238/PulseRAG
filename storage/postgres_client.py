
CREATE_TABLES_SQL = '''
CREATE TABLE IF NOT EXISTS conversations (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query           TEXT NOT NULL,
