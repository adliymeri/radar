ALTER TABLE buyer_requests
DROP CONSTRAINT IF EXISTS buyer_requests_matched_listing_id_fkey;

DROP INDEX IF EXISTS idx_buyer_requests_matched_listing_id;

ALTER TABLE buyer_requests
RENAME COLUMN matched_listing_id TO matched_listing_ids;

ALTER TABLE buyer_requests
ALTER COLUMN matched_listing_ids TYPE UUID[]
USING (
    CASE
        WHEN matched_listing_ids IS NULL THEN ARRAY[]::UUID[]
        ELSE ARRAY[matched_listing_ids]
    END
);

ALTER TABLE buyer_requests
ALTER COLUMN matched_listing_ids SET DEFAULT ARRAY[]::UUID[];

UPDATE buyer_requests
SET matched_listing_ids = ARRAY[]::UUID[]
WHERE matched_listing_ids IS NULL;

CREATE INDEX idx_buyer_requests_matched_listing_ids
ON buyer_requests USING GIN (matched_listing_ids);