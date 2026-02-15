CREATE TABLE IF NOT EXISTS migrations (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL UNIQUE,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO migrations (filename) VALUES ('20251101T191200-create-tables.sql');
INSERT INTO migrations (filename) VALUES ('20260215T000000-create-migrations-table.sql');