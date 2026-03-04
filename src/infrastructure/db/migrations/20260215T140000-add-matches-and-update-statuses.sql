-- Migration: Add matches table and update buyer_requests status constraint
-- Date: 2026-02-15

-- Drop old constraint
ALTER TABLE buyer_requests DROP CONSTRAINT IF EXISTS buyer_requests_status_check;

-- Add new constraint with additional statuses
ALTER TABLE buyer_requests
ADD CONSTRAINT buyer_requests_status_check 
CHECK (status IN ('active', 'paused', 'matched'));

-- Set default to 'active' instead of 'pending'
ALTER TABLE buyer_requests ALTER COLUMN status SET DEFAULT 'active';

-- Update existing 'pending' records to 'active'
UPDATE buyer_requests SET status = 'active' WHERE status = 'pending';

-- Create matches table
CREATE TABLE matches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    buyer_id UUID NOT NULL REFERENCES buyers(id) ON DELETE CASCADE,
    seller_id UUID NOT NULL REFERENCES sellers(id) ON DELETE CASCADE,
    listing_id UUID NOT NULL REFERENCES listings(id) ON DELETE CASCADE,
    request_id UUID NOT NULL REFERENCES buyer_requests(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL DEFAULT 'notified', -- 'notified', 'contacted', 'rejected'
    notified_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    contacted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(listing_id, request_id) -- Prevent duplicate matches
);

-- Indexes for matches
CREATE INDEX idx_matches_buyer_id ON matches(buyer_id);
CREATE INDEX idx_matches_seller_id ON matches(seller_id);
CREATE INDEX idx_matches_listing_id ON matches(listing_id);
CREATE INDEX idx_matches_request_id ON matches(request_id);
CREATE INDEX idx_matches_status ON matches(status);
CREATE INDEX idx_matches_notified_at ON matches(notified_at);

-- Add constraint
ALTER TABLE matches
ADD CONSTRAINT matches_status_check 
CHECK (status IN ('notified', 'contacted', 'rejected'));

INSERT INTO migrations (filename) VALUES ('20260215T140000-add-matches-and-update-statuses.sql');